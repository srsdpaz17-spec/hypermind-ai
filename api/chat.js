import OpenAI from "openai";
import { loadMemory, saveMemory } from "../src/memory.js";
import { analyzeMessage } from "../src/hypermind-ai.js";
import { monitorStats } from "../src/monitor.js";

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
      ]
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

    const monitor = monitorStats ? monitorStats(message, response) : null;

    res.status(200).json({ response, monitor });
  } catch (e) {
    console.error("Erro na API /api/chat:", e);
    res.status(500).json({ error: e?.message || "Erro interno" });
  }
}
