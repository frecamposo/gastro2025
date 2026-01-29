
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un producto en un taller específico
class ProductoTaller(BaseModel):
    id_producto: int
    id_taller: int
    cod_agrupador: int
    cantidad: float
    nom_unidad_medida: Optional[str]
    nom_producto: Optional[str]
    cod_categ_producto: Optional[int]
    nom_categ_producto: Optional[str]
    nom_agrupador: Optional[str]
    obs: Optional[str]
    precio: Optional[int]
    total: Optional[int]
    
class ObservacionProductoTaller(BaseModel):
    id_producto: int
    id_taller: int
    obs: Optional[str]