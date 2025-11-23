
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un producto en la bodega
class Bodega(BaseModel):
    id_producto: Optional[int]
    nom_producto: str
    precio: int
    cantidad: Optional[float]
    stock_critico: Optional[float]
    cod_unidad_medida: int
    cod_categ_producto: int
    nom_unidad_medida: Optional[str]
    nom_categ_producto: Optional[str]


class CabeceraBodegaIn(BaseModel):
    id_ingreso: Optional[int]
    fecha_ingreso: str
    factura: int
    responsable: str
    proveedor: str 


class DetalleFactura(BaseModel):
    id_detalle: Optional[int]
    id_producto: int
    nombre: Optional[str]
    precio: int
    cantidad: float
    total: Optional[int]
    

class ActualizarStockProducto(BaseModel):
    id_producto: int
    cantidad: int
    
class ActualizarProducto(BaseModel):
    id_producto: int
    stock_critico: int
    cantidad:int
        
class DetalleIngreso(BaseModel):
    id_detalle: Optional[int]
    id_producto: int
    nombre: Optional[str]
    precio: int
    cantidad: float
    total: Optional[int]
    
class CabeceraRetiro(BaseModel):
    id_retiro: Optional[int]
    fecha: str
    nombre_asig: str
    codigo_asig: str
    seccion: str
    responsable_retiro: str
    responsable_entrega: str

class DetalleRetiro(BaseModel):
    id_retiro: Optional[int]
    id_producto: int
    nombre: Optional[str]
    precio: int
    cantidad: float
    total: Optional[int]
    
    
class DocenteTaller(BaseModel):
    id_usuario: int
    nom_usuario: str
    sigla_taller: str
    seccion:str
    id_taller: int
    titulo_preparacion: str
    semana: int
  