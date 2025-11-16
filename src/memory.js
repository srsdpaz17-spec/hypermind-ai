import fs from "fs";
import path from "path";

const isProduction = process.env.NODE_ENV === "production";
// Em producao em Vercel a area /tmp é gravavel (mas efêmera). Para persistência real use DB/KV.
const MEMORY_PATH = isProduction
  ? path.join("/tmp", "memory.json")
  : path.join(process.cwd(), "src", "memory.json");

export function loadMemory() {
  try {
    if (!fs.existsSync(MEMORY_PATH)) return { conversations: [] };
    const data = fs.readFileSync(MEMORY_PATH, "utf-8");
    return JSON.parse(data);
  } catch (err) {
    console.warn("loadMemory error:", err?.message || err);
    return { conversations: [] };
  }
}

export function saveMemory(memory) {
  try {
    fs.writeFileSync(MEMORY_PATH, JSON.stringify(memory, null, 2));
  } catch (err) {
    // Não propaga para evitar quebrar a rota; apenas loga para diagnóstico.
    console.warn("saveMemory error (memory not saved):", err?.message || err);
  }
}
