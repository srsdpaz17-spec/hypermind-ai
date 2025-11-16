export function monitorStats(input, output) {
  return {
    tokensEntrada: input.length,
    tokensSaida: output.length,
    crescimento: output.length - input.length,
    data: new Date().toISOString()
  };
}
