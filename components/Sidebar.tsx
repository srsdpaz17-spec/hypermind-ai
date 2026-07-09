import Link from "next/link";

export default function Sidebar() {
  return (
    <aside
      style={{
        width: "260px",
        background: "#020617",
        color: "#fff",
        padding: "30px",
        minHeight: "100vh",
      }}
    >
      <h2 style={{ marginBottom: "40px" }}>HyperMind AI</h2>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "18px",
        }}
      >
        <Link href="/dashboard">🏠 Dashboard</Link>

        <Link href="/chat">🤖 IA</Link>

        <Link href="/crm">👥 CRM</Link>

        <Link href="/vendas">💰 Vendas</Link>

        <Link href="/configuracoes">⚙ Configurações</Link>
      </nav>
    </aside>
  );
}