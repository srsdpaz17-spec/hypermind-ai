async function sendMessage() {
  const message = document.getElementById("msg").value;

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  document.getElementById("response").innerText =
    "Resposta:\n" + data.response +
    "\n\nMonitor:\n" + JSON.stringify(data.monitor, null, 2);
}
