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

  try {
    const { message } = req.body;

    const memory = loadMemory();
    const aiAnalysis = analyzeMessage(message, memory);

    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: aiAnalysis.systemPrompt },
        { role: "user", content: message }
      ]
    });

    const response = completion.choices[0].message.content;

    memory.conversations.push({ input: message, output: response });
    saveMemory(memory);

    const monitor = monitorStats(message, response);

    res.status(200).json({
      response,
      monitor
    });

  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
