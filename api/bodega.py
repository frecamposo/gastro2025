
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.producto import Producto
from models.bodega import *
from models.usuario import Usuario
from database import get_db_connection
from api.perfil import perfil_usuario
from infrastructure.constants import Const

from datetime import datetime

router = fastapi.APIRouter()


@router.get("/api/bodega/lista/{id_usuario}", summary="Recupera los productos desde la bodega", tags=["Bodega"])
async def productos_bodega(id_usuario: int):
    productos: List[Bodega] = []    

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return productos
    
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return productos

    query = " \
        select p.id_producto as id_producto, \
            p.nom_producto as nom_producto, \
            p.precio as precio, \
            p.cantidad as cantidad, \
            p.stock_critico as stock_critico, \
            p.cod_unidad_medida as cod_unidad_medida, \
            p.cod_categ_producto as cod_categ_producto, \
            um.nom_unidad_medida as nom_unidad_medida, \
            cp.nom_categ_producto as nom_categ_producto \
        from bodega p \
        join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
        join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
        order by p.nom_producto asc"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = ()
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchall()

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    # Armamos el diccionario de salida
    producto: Bodega = None
    productos: List[Bodega] = []
    for row in result:
        producto = Bodega(id_producto=row[0],
                            nom_producto=row[1],
                            precio=row[2],
                            cantidad=row[3],
                            stock_critico=row[4],
                            cod_unidad_medida=row[5],
                            cod_categ_producto=row[6],
                            nom_unidad_medida=row[7],
                            nom_categ_producto=row[8])
        productos.append(producto)

    return productos


# @router.delete("/api/producto/eliminar/{id_producto}/{id_usuario}", response_model=dict, summary="Elimina un producto para un determinado usuario", tags=["Productos"])
# async def asignatura_eliminar(id_producto: int, id_usuario: int):

#     # Determinamos el perfil del usuario para determinar qué información puede borrar
#     perfil = await perfil_usuario(id_usuario)
#     usuarios: List[Usuario] = []
#     # Si todo está correcto, Retornamos la respuesta de la API
#     if not perfil:
#         return usuarios
#     # Perfil docente no debe ver nada
#     if perfil.cod_perfil == Const.K_DOCENTE.value:
#         return {
#             "id_producto": id_producto,
#             "eliminado": False,
#             "msg_error": "Usuario con perfil Docente no tiene acceso a eliminar"
#         }

#     db = await get_db_connection()
#     if db is None:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

#     try:
#         query = "delete from producto where id_producto = %s"

#         values = (id_producto)
#         async with db.cursor() as cursor:
#             await cursor.execute(query, values)
#             await db.commit()

#             return {
#                 "id_producto": id_producto,
#                 "eliminado": True,
#                 "msg_error": None
#             }

#     except aiomysql.Error as e:
#         error_message = str(e)
#         # Controlamos de manera especial el error de integridad de datos
#         if "1451" in error_message:
#             return {
#                 "id_producto": id_producto,
#                 "eliminado": False,
#                 "msg_error": "Producto no se puede eliminar por integridad de datos"
#             }
#         if "Connection" in error_message:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

#     except Exception as e:
#         error_message = str(e)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

#     finally:
#         db.close()

#     return {
#         "id_producto": id_producto,
#         "eliminado": True
#     }


@router.get("/api/bodega/{id_producto}/{id_usuario}", response_model=Bodega, summary="Recupera un producto en base a su Id", tags=["Bodega"])
async def producto_bodega_get(id_producto: int, id_usuario: int):
    producto: Bodega = {
        "id_producto": 0,
        "nom_producto": "",
        "precio": 0,
        "cantidad": 0,
        "stock_critico": 0,
        "cod_unidad_medida": 0,
        "cod_categ_producto": 0,
        "nom_unidad_medida": "",
        "nom_categ_producto": "",
    }

    # Si id_producto = 0 se asume que es nuevo
    if id_producto == 0:
        return producto

    # Determinamos el perfil del usuario conectado para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return producto
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return producto

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select p.id_producto as id_producto, \
                p.nom_producto as nom_producto, \
                p.precio as precio, \
                p.cantidad as cantidad, \
                p.stock_critico as stock_critico,  \
                p.cod_unidad_medida as cod_unidad_medida, \
                p.cod_categ_producto as cod_categ_producto, \
                um.nom_unidad_medida as nom_unidad_medida, \
                cp.nom_categ_producto as nom_categ_producto \
            from bodega p \
            join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
            join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
            where p.id_producto = %s"

        values = (id_producto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()
            if not result:
                return producto

            producto = Bodega(id_producto=result[0],
                                nom_producto=result[1],
                                precio=result[2],
                                cantidad=result[3],
                                stock_critico=result[4],
                                cod_unidad_medida=result[5],
                                cod_categ_producto=result[6],
                                nom_unidad_medida=result[7],
                                nom_categ_producto=result[8],)
            return producto

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

    finally:
        db.close()

@router.put("/api/bodega/{id_usuario}/", response_model=Bodega, summary="Modificar un producto de la bodega", tags=["Bodega"])
async def modificar_producto_bodega(producto: Bodega, id_usuario: int) -> Producto:

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update bodega \
                set precio = %s, \
                    cantidad = %s, \
                    stock_critico=%s \
            where id_producto = %s"
        values = (producto.precio,
                  producto.cantidad,
                  producto.stock_critico,
                  producto.id_producto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return producto


# aumentar el stock de productos en bodega (OK)
@router.post("/api/bodega/mas/{id_usuario}/", response_model=List[ActualizarStockProducto], summary="Aumenta el Stock de productos en la bodega", tags=["Bodega"])
async def modificar_producto_bodega_mas(productos: List[ActualizarStockProducto], id_usuario: int) -> List[ActualizarStockProducto]:

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        for p in productos:
            query = " \
                update bodega \
                    set cantidad = cantidad + %s \
                where id_producto = %s"
            values = (p.cantidad,
                    p.id_producto)
        
            async with db.cursor() as cursor:
                await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return productos

@router.post("/api/bodega/cabecera_mas/{id_usuario}/", response_model=List[DetalleIngreso], summary="Aumenta el Stock de productos en la bodega", tags=["Bodega"])
async def ingreso_producto_bodega_mas(productos: List[DetalleIngreso], id_usuario: int) -> List[DetalleIngreso]:
    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        for p in productos:
            query = " \
                insert into detalle_ingreso(id_detalle, id_producto, nombre, precio, cantidad, total) \
                    values( %s, %s, %s, %s, %s, %s) "
            values = (p.id_detalle,p.id_producto,p.nombre,p.precio,p.cantidad,p.total)
            async with db.cursor() as cursor:
                await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")
    finally:
        db.close()

    return productos

@router.post("/api/bodega/cabecera_in/", response_model=CabeceraBodegaIn, summary="Agregar Cabecera con el detalle del ingreso del producto a bodega", tags=["Bodega"])
async def insertar_cabecera_ingreso(cabecera: CabeceraBodegaIn) -> CabeceraBodegaIn:
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
    try:
        formato = "%Y-%m-%d"
        objeto_fecha = datetime.strptime(cabecera.fecha_ingreso, formato)
        query = " \
            insert into cabecera_ingreso ( \
                fecha, \
                factura, \
                responsable_ing, \
                proveedor) \
            values (%s, \
                %s, \
                %s, \
                %s)"
        values = (objeto_fecha,
                  cabecera.factura,
                  cabecera.responsable,
                  cabecera.proveedor)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            cabecera.id_ingreso = cursor.lastrowid

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()
    return cabecera

# disminuir el stock de productos en bodega
@router.put("/api/bodega/menos/{id_usuario}/", response_model=List[ActualizarStockProducto], summary="Disminuye el Stock de productos en la bodega", tags=["Bodega"])
async def modificar_producto_bodega_menos(productos: List[ActualizarStockProducto], id_usuario: int) -> List[ActualizarStockProducto]:

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        for p in productos:
            query = " \
                update bodega \
                    set cantidad = cantidad - %s \
                where id_producto = %s"
            values = (p.cantidad,
                    p.id_producto)
        
            async with db.cursor() as cursor:
                await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return productos

@router.post("/api/bodega/cabecera_menos/{id_usuario}/", response_model=CabeceraRetiro, summary="Disminuye el Stock de productos en la bodega, cabecera del retiro", tags=["Bodega"])
async def retiro_producto_bodega_cabecera(productos: CabeceraRetiro, id_usuario: int) -> CabeceraRetiro:
    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
            formato = "%Y-%m-%d"
            objeto_fecha = datetime.strptime(productos.fecha, formato)
            query = " \
                insert into retiro(fecha, nombre_asig, codigo_asig,seccion,responsable_retiro,responsable_entrega) \
                    values( %s, %s, %s, %s, %s, %s) "
            values = (objeto_fecha,
                      productos.nombre_asig,
                      productos.codigo_asig,
                      productos.seccion,
                      productos.responsable_retiro,
                      productos.responsable_entrega)
            async with db.cursor() as cursor:
                await cursor.execute(query, values)
                productos.id_retiro = cursor.lastrowid

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos.  {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")
    finally:
        db.close()
    return productos


@router.post("/api/bodega/detalle_retiro/{id_usuario}/", response_model=List[DetalleIngreso], summary="Almacena el detalle del retiro de bodega", tags=["Bodega"])
async def retiro_producto_bodega(productos: List[DetalleIngreso], id_usuario: int) -> List[DetalleIngreso]:
    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        for p in productos:
            query = " \
                insert into detalle_retiro(id_detalle, id_producto, nombre, precio, cantidad, total) \
                    values( %s, %s, %s, %s, %s, %s) "
            values = (p.id_detalle,p.id_producto,p.nombre,p.precio,p.cantidad,p.total)
            async with db.cursor() as cursor:
                await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")
    finally:
        db.close()

    return productos


# actualizar la cantidad o el stock critico de productos en bodega
@router.put("/api/bodega/producto_actualizar/{id_usuario}/", response_model=ActualizarProducto, summary="Modifica cantidad y stock de producto", tags=["Bodega"])
async def modificar_producto_bodega_menos(producto: ActualizarProducto, id_usuario: int) -> ActualizarStockProducto:
    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
            query = " \
                update bodega \
                    set cantidad = %s, stock_critico = %s  \
                where id_producto = %s"
            values = (producto.cantidad,producto.stock_critico,
                    producto.id_producto)
        
            async with db.cursor() as cursor:
                await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return producto


@router.get("/api/lista_docentes_talleres/{id}", response_model=List[DocenteTaller], summary="Recupera la lista de Docente con sus respectivos talleres ", tags=["Bodega"])
async def lista_docentes_talleres(id: int) -> List[DocenteTaller]:
    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id)
    docentes: List[DocenteTaller] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return []
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return []

    # Dependiendo del perfil, filtramos por carrera o no
    query: str = None
    query = "select u.id_usuario,concat(u.nom , ' ',u.primer_apellido , ' ' , u.segundo_apellido) as usuario, pt.sigla,pt.seccion,pt.id_taller,t.titulo_preparacion,t.semana from usuario u inner JOIN prog_taller pt on pt.id_usuario=u.id_usuario inner join taller t on t.id_taller=pt.id_taller INNER join config_taller ct on ct.id_taller=t.id_taller GROUP BY u.id_usuario,concat(u.nom , ' ',u.primer_apellido , ' ' , u.segundo_apellido) , pt.sigla,pt.seccion,pt.id_taller,t.titulo_preparacion,t.semana order by 1,3,4; "
    print(query)            
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
    try:            
        values = ()
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchall()

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    # Armamos el diccionario de salida
    profesor: DocenteTaller = None
    
    for row in result:
        profesor = DocenteTaller(id_usuario=row[0],
                          nom_usuario=row[1],
                          sigla_taller=row[2],
                          seccion=row[3],
                          id_taller=row[4],
                          titulo_preparacion=row[5],
                          semana=row[6]
                          )
        docentes.append(profesor)

    return docentes

