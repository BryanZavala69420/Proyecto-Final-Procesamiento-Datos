import axios from "axios";
import React, { useEffect, useState } from "react";

import { Link } from "react-router-dom";



function Tabla2() {
    const [usuarios, setUsuarios] = useState([]);
    const [cargando, setCargando] = useState(true);


    useEffect(() => {
        axios
            .get("http://localhost:8081/sas")
            .then((response) => {
                setUsuarios(response.data);
                setCargando(false);
            })
            .catch((error) => {
                console.error("Error al obtener los usuarios", error);
                setCargando(false);
            });


    }, []);



    if (cargando) return <p> Cargando usuarios... </p>;

    return (
        <div>
            <div className="Titulo">
                <h1> Tabla donde se daran los datos del web scrapping </h1>

            </div>

            <div className="Tabla">

                <table className="Tabla_Usuarios">
                    <thead>
                        <tr>
                            <th> sku_id </th>
                            <th> id_usuario </th>
                            <th> nombre_ciudad </th>
                            <th> fabricante </th>
                            <th> consumo_energetico </th>
                            <th> precio_por_millon </th>
                            <th> objeto premium</th>
                            <th> numero_purikya</th>
                       
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
                                <tr key={mapear.id_usuario}>
                                    <td>{mapear.sku_id}</td>
                                    <td>{mapear.id_usuario}</td>
                                    <td>{mapear.nombre_ciudad}</td>
                                    <td>{(mapear.fabricante)}</td>
                                    <td>{mapear.consumo_energetico}</td>
                                    <td> {mapear.precio_por_millon}</td> 
                                    <td> {mapear.objeto_premium}</td>
                                    <td>{mapear.numero_purikya}</td>



                                </tr>
                            ))


                        )}
                    </tbody>

                </table>




            </div>




        </div>



    )



}

export default Tabla2;