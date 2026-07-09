export default function Dashboard() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#0F172A",
        color: "white",
        display: "flex",
      }}
    >
      <aside
        style={{
          width: 260,
          background: "#020617",
          padding: 25,
        }}
      >
        <h2>HyperMind</h2>

        <hr />

        <p>🏠 Dashboard</p>

        <p>💬 IA</p>

        <p>👥 CRM</p>

        <p>📈 Vendas</p>

        <p>⚙ Configurações</p>
      </aside>

      <section
        style={{
          flex: 1,
          padding: 40,
        }}
      >
        <h1
          style={{
            fontSize: 42,
          }}
        >
          Dashboard
        </h1>

        <br />

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3,1fr)",
            gap: 20,
          }}
        >
          <div
            style={{
              background: "#1E293B",
              padding: 30,
              borderRadius: 15,
            }}
          >
            <h2>Clientes</h2>
            <h1>0</h1>
          </div>

          <div
            style={{
              background: "#1E293B",
              padding: 30,
              borderRadius: 15,
            }}
          >
            <h2>Vendas</h2>
            <h1>R$ 0,00</h1>
          </div>

          <div
            style={{
              background: "#1E293B",
              padding: 30,
              borderRadius: 15,
            }}
          >
            <h2>IA</h2>
            <h1>Online</h1>
          </div>
        </div>
      </section>
    </main>
  );
}