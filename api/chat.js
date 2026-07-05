import OpenAI from "openai";
import { loadMemory, saveMemory } from "../src/memory.js";
import { analyzeMessage } from "../src/hypermind-ai.js";
import { runMonitor } from "../src/monitor.js";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método inválido" });
  }

  if (!process.env.OPENAI_API_KEY) {
    console.error("OPENAI_API_KEY não está configurada.");
    return res.status(500).json({ error: "Chave de API não configurada no ambiente" });
  }

  try {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Campo 'message' é obrigatório" });

    const memory = loadMemory();

    // suporta analyzeMessage síncrono ou que retorne Promise
    const aiAnalysis = await Promise.resolve(analyzeMessage(message, memory));

    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: aiAnalysis.systemPrompt || "" },
        { role: "user", content: message }
      ],
      temperature: aiAnalysis.temperature ?? 0.7,
      max_tokens: aiAnalysis.max_tokens ?? 800
    });

    const response = completion?.choices?.[0]?.message?.content ?? "";

    // Atualiza memória local (pode falhar silenciosamente em serverless)
    try {
      memory.conversations = memory.conversations || [];
      memory.conversations.push({ input: message, output: response, createdAt: new Date().toISOString() });
      saveMemory(memory);
    } catch (err) {
      console.warn("Erro ao salvar memória (não bloqueante):", err?.message || err);
    }

    // Executa monitor interno (gera crítica, sugestões e self_reply)
    let monitorResult = null;
    try {
      monitorResult = await runMonitor(client, message, response, memory);
      // salve resultado do monitor na memória para análise posterior
      try {
        memory.monitor = memory.monitor || [];
        memory.monitor.push({ ts: new Date().toISOString(), result: monitorResult });
        saveMemory(memory);
      } catch (err) {
        console.warn('Falha ao salvar monitor na memória:', err?.message || err);
      }
    } catch (err) {
      console.warn('runMonitor falhou:', err?.message || err);
      monitorResult = { error: err?.message || String(err) };
    }

    // Opcional: ciclo único de self-reply limitado — só se o monitor sugerir
    let finalResponse = response;
    try {
      const selfReply = monitorResult?.parsed?.self_reply || null;
      const maxSelfReplies = 1;
      let selfReplies = 0;

      if (selfReply && typeof selfReply === 'string' && selfReplies < maxSelfReplies) {
        selfReplies++;
        const followup = await client.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: [
            { role: 'system', content: 'You are the assistant. Reply concisely to the monitoring self_reply and improve the previous answer if applicable.' },
            { role: 'user', content: selfReply }
          ],
          temperature: 0.2,
          max_tokens: 250
        });
        const followupText = followup?.choices?.[0]?.message?.content ?? '';
        if (followupText) {
          finalResponse = response + '\n\n[Self-update]\n' + followupText;
          try {
            memory.conversations.push({ input: '[self_reply]', output: followupText, createdAt: new Date().toISOString() });
            saveMemory(memory);
          } catch (err) {
            console.warn('Falha ao salvar followup na memória:', err?.message || err);
          }
        }
      }
    } catch (err) {
      console.warn('Erro durante self-reply:', err?.message || err);
    }

    res.status(200).json({ response: finalResponse, monitor: monitorResult });
  } catch (e) {
    console.error("Erro na API /api/chat:", e);
    res.status(500).json({ error: e?.message || "Erro interno" });
  }
}
