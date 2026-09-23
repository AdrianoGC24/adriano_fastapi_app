from sqlmodel import SQLModel, Field
from pydantic import field_validator

categories = [
    "monitores",
    "mauses",
    "teclados"
]
class Product(SQLModel, table=True):
    __tablename__ = "app_inv_products"

    id: int | None = Field(primary_key=True, default=None)
    name: str
    price: float = Field(ge=10000)
    category: str 
    quantity: int = Field(ge=1)
    
    
    @field_validator("category", mode="before")
    @classmethod
    def validar_categoria(cls, valor: str) -> str:
        if isinstance(valor, str):
            valor_limpio = valor.lower().strip()
            if valor_limpio in categories:
                return valor_limpio
        raise ValueError(
            f"Esta categoría no existe. categorias validas: {categories}"
            )