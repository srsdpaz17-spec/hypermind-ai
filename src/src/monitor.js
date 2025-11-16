export function monitorStats(input, output) {
  return {
    inputSize: input.length,
    outputSize: output.length,
    timestamp: new Date().toISOString()
  };
}
