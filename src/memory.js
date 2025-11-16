import fs from "fs";

const path = "./models/memory.json";

export function loadMemory() {
  if (!fs.existsSync(path)) {
    fs.writeFileSync(path, JSON.stringify({ conversations: [] }, null, 2));
  }
  const content = fs.readFileSync(path);
  return JSON.parse(content);
}

export function saveMemory(memory) {
  fs.writeFileSync(path, JSON.stringify(memory, null, 2));
}
