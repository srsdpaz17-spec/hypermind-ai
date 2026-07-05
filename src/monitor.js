export async function runMonitor(client, message, response, memory) {
  // Estatísticas básicas
  const stats = {
    inputLength: message ? message.length : 0,
    responseLength: response ? response.length : 0,
    timestamp: new Date().toISOString(),
  };

  // Se não há cliente OpenAI configurado, retorne só as estatísticas
  if (!client || !client.chat || !process.env.OPENAI_API_KEY) {
    return { stats, note: 'no-client' };
  }

  try {
    // Prompt para o monitor interno: criticar, sugerir melhorias e gerar um self_reply
    const systemPrompt = `You are an internal monitoring agent for an assistant. Your job is to:
1) Provide a short, actionable critique of the assistant's response (1-2 sentences).
2) Provide up to 3 concrete suggestions to improve future responses (array of strings).
3) Produce a brief "self_reply" — a message the assistant could send to itself to further the conversation or to correct/improve the prior response.

Return a JSON object EXACTLY with the fields: {"critique":string, "suggestions": [string,...], "self_reply": string} and nothing else. Be concise.`;

    const userContent = `User message:\n${message}\n\nAssistant response:\n${response}`;

    const completion = await client.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userContent }
      ],
      temperature: 0.2,
      max_tokens: 300
    });

    const content = completion?.choices?.[0]?.message?.content ?? '';

    // Tentar parsear JSON estrito do conteúdo
    let parsed = null;
    try {
      parsed = JSON.parse(content);
    } catch (err) {
      // fallback: tentar extrair um bloco JSON se o modelo adicionou texto antes/depois
      const match = content.match(/\{[\s\S]*\}/);
      if (match) {
        try {
          parsed = JSON.parse(match[0]);
        } catch (err2) {
          parsed = null;
        }
      }
    }

    const monitor = {
      stats,
      raw: content,
      parsed,
      model: completion?.model || null,
    };

    return monitor;
  } catch (err) {
    return { stats, error: err?.message || String(err) };
  }
}
