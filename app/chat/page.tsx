"use client";

import { useState } from "react";

export default function Chat() {
  const [mensagem, setMensagem] = useState("");
  const [historico, setHistorico] = useState<
    { autor: string; texto: string }[]
  >([]);

  async function enviar() {
    if (!mensagem.trim()) return;

    const texto = mensagem;

    setHistorico((h) => [...h, { autor: "Você", texto }]);

    setMensagem("");

    try {
      const resposta = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: texto,
        }),
      });

      const data = await resposta.json();

      setHistorico((h) => [
        ...h,
        {
          autor: "HyperMind",
          texto: data.reply ?? "Sem resposta",
        },
      ]);
    } catch {
      setHistorico((h) => [
        ...h,
        {
          autor: "HyperMind",
          texto: "Erro ao conectar com a IA.",
        },
      ]);
    }
  }

  return (
    <main
      style={{
        padding: 40,
        background: "#0F172A",
        minHeight: "100vh",
        color: "white",
      }}
    >
      <h1>HyperMind IA</h1>

      <div
        style={{
          marginTop: 30,
          background: "#1E293B",
          borderRadius: 12,
          padding: 20,
          minHeight: 400,
        }}
      >
        {historico.map((item, i) => (
          <div key={i} style={{ marginBottom: 15 }}>
            <strong>{item.autor}</strong>

            <p>{item.texto}</p>
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: 20,
          display: "flex",
          gap: 10,
        }}
      >
        <input
          value={mensagem}
          onChange={(e) => setMensagem(e.target.value)}
          placeholder="Digite sua pergunta..."
          style={{
            flex: 1,
            padding: 15,
            borderRadius: 8,
            border: "none",
          }}
        />

        <button
          onClick={enviar}
          style={{
            padding: "15px 25px",
            cursor: "pointer",
          }}
        >
          Enviar
        </button>
      </div>
    </main>
  );
}