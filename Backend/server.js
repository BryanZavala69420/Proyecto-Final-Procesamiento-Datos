const express = require("express");
const mysql = require("mysql");
const cors = require("cors");
const app = express();
app.use(cors());

// Conexión con reconexión automática
function conectar() {
  const BaseDatos = mysql.createConnection({
    host: "localhost",
    user: "ernesto",
    password: "030224",
    database: "ventas",
  });

  BaseDatos.connect((err) => {
    if (err) {
      console.error("Error conectando, reintentando en 2s...", err);
      setTimeout(conectar, 2000);
      return;
    }
    console.log("Conectado a MariaDB");
  });

  BaseDatos.on("error", (err) => {
    console.error("Error de BD:", err);
    if (err.fatal) conectar(); // reconecta si muere
  });

  return BaseDatos;
}

let BaseDatos = conectar();

app.get("/sus", (req, res) => {
  BaseDatos.query(
    "SELECT id_transaccion, id_cliente, monto, fecha, id_tienda FROM ventas_chingonas",
    (err, result) => {
      if (err) return res.status(500).json([]);
      return res.json(result);
    },
  );
});

app.get("/sas", (req, res) => {
  BaseDatos.query("SELECT * FROM ventas LIMIT 100", (err, result) => {
    if (err) return res.status(500).json([]);
    return res.json(result);
  });
});

app.listen(8081, () => console.log("Servidor en puerto 8081"));
