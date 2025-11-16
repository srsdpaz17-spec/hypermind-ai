export function analyzeMessage(message, memory) {

  const lastFive = memory.conversations.slice(-5);

  return {
    systemPrompt: `
Você é uma IA evolutiva chamada HyperMind.
Aprenda com o histórico, adapte sua comunicação e evolua em clareza e estratégia.

Últimas conversas para contexto:
${JSON.stringify(lastFive, null, 2)}
    `
  };
}
