import OpenAI from "openai";
import { loadMemory, saveMemory } from "../src/memory.js";
import { analyzeMessage } from "../src/hypermind-ai.js";
import { monitorStats } from "../src/monitor.js";

export const config = {
  runtime: "edge"
};

export default async function handler(req) {
  try {
    const { message } = await req.json();

    const client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });

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

    return new Response(
      JSON.stringify({ response, monitor }),
      { status: 200 }
    );

  } catch (e) {
    return new Response(
      JSON.stringify({ error: e.message }),
      { status: 500 }
    );
  }
}
