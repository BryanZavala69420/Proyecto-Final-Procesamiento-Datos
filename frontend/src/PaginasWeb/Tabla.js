import axios from "axios";
import React, { useEffect, useState } from "react";

import { Link } from "react-router-dom";



function Tabla() {
    const [usuarios, setUsuarios] = useState([]);
    const [cargando, setCargando] = useState(true);


    useEffect(() => {
        axios
            .get("http://localhost:8081/sus")
            .then((response) => {
                setUsuarios(response.data);
                setCargando(false);
            })
            .catch((error) => {
                console.error("Error al obtener los usuarios", error);
                setCargando(false);
            });


    }, []);


    const formatearFecha = (fechaISO) => {
        const fecha = new Date(fechaISO);

        return fecha.toLocaleDateString("es-MX", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        });
    };

    if (cargando) return <p> Cargando usuarios... </p>;

    return (
        <div>
            <div className="Titulo">
                <h1> Hola mundo</h1>
            </div>

            <div className="Tabla">

                <table className="Tabla_Usuarios">
                    <thead>
                        <tr>
                            <th> Id_transaccion </th>
                            <th> Id_Cliente </th>
                            <th> Monto </th>
                            <th> Fecha </th>
                            <th> Id_Tienda </th>
                        </tr>

                    </thead>

                    <tbody>
                        {usuarios.length === 0 ? (

                            <tr>
                                <td colSpan="5">
                                    No hay usuarios registrados
                                </td>
                            </tr>

                        ) : (

                            usuarios.map((mapear) => (
                                <tr key={mapear.id_transaccion}>
                                    <td>{mapear.id_transaccion}</td>
                                    <td>{mapear.id_cliente}</td>
                                    <td>${mapear.monto}</td>
                                    <td>{formatearFecha(mapear.fecha)}</td>
                                    <td>{mapear.id_tienda}</td>
                                </tr>
                            ))


                        )}
                    </tbody>

                </table>




            </div>



        </div>



    )



}

export default Tabla;