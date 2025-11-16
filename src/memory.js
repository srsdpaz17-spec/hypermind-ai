import fs from "fs";

const MEMORY_PATH = "./src/memory.json";

export function loadMemory() {
  try {
    const data = fs.readFileSync(MEMORY_PATH, "utf-8");
    return JSON.parse(data);
  } catch {
    return { conversations: [] };
  }
}

export function saveMemory(memory) {
  fs.writeFileSync(MEMORY_PATH, JSON.stringify(memory, null, 2));
}
