import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import Card from "@/components/Card";

export default function Dashboard() {
  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0F172A",
      }}
    >
      <Sidebar />

      <div
        style={{
          flex: 1,
        }}
      >
        <Header />

        <main
          style={{
            padding: 30,
          }}
        >
          <h1
            style={{
              color: "white",
              marginBottom: 30,
            }}
          >
            Dashboard
          </h1>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3,1fr)",
              gap: 20,
            }}
          >
            <Card titulo="Clientes" valor="0" />

            <Card titulo="Vendas" valor="R$ 0,00" />

            <Card titulo="IA" valor="Online" />
          </div>
        </main>
      </div>
    </div>
  );
}