interface Props {
  titulo: string;
  valor: string;
}

export default function Card({ titulo, valor }: Props) {
  return (
    <div
      style={{
        background: "#1E293B",
        borderRadius: 15,
        padding: 25,
      }}
    >
      <h3>{titulo}</h3>

      <h1
        style={{
          marginTop: 20,
          fontSize: 35,
        }}
      >
        {valor}
      </h1>
    </div>
  );
}