export function analyzeMessage(message, memory) {
  const lastMessages = memory.conversations.slice(-5);

  return {
    systemPrompt: `
Você é uma IA rápida, direta, inteligente, que responde de forma profissional.
Histórico recente do usuário:
${lastMessages.map(c => "- " + c.input).join("\n")}
`
  };
}
