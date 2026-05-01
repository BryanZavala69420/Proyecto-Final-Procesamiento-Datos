//dependencias para que pueda correr la madre esta
const express = require('express');
const mysql = require('mysql');
const cors = require('cors');

const app = express();
app.use(cors());

//base de datos, conexion
const BaseDatos = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: '',
    database: "ventas"
});
// puerto
const port = 8081;

app.get('/sus', (req, res)=>{

    const Consulta_SQL = "SELECT  id_transaccion, id_cliente, monto, fecha, id_tienda FROM ventas_chingonas"
    
    BaseDatos.query(Consulta_SQL, (err, result) => {
        if(err){
            return res.json(err);
        }else{
            return res.json(result);
        }
    });


});

app.get('/sas', (req, res)=>{

    const Consulta_SQL = "SELECT sku_id, id_usuario, nombre_ciudad, fabricante, consumo_energetico, precio_por_millon, objeto_premium, numero_purikya FROM hola"
    
    BaseDatos.query(Consulta_SQL, (err, result) => {
        if(err){
            return res.json(err);
        }else{

            return res.json(result);

        }
    });


});





app.listen(port, () => {
    console.log('conectandose en el puerto 8081, y en el puerto 3001');
});
