from sqlmodel import SQLModel, Field
from pydantic import field_validator

CATEGORIES = [
    "monitores",
    "mauses",
    "teclados"
]


class ProductBase(SQLModel):
    name: str = Field(min_length=1, description="Nombre del producto")
    price: float = Field(ge=10000, description="Precio mínimo del producto (al menos 10.000)")
    category: str = Field(min_length=1, description="Categoría del producto")
    quantity: int = Field(ge=1, description="Cantidad en stock (mínimo 1 unidad)")
    # actualización carga de imagenes para almacenar en s3
    image_url: str | None = Field(default=None, description="URL publica de la imagen en s3")

    @field_validator("name")
    @classmethod
    def validar_nombre_no_vacio(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío ni contener solo espacios en blanco")
        return valor.strip()

    @field_validator("category", mode="before")
    @classmethod
    def validar_categoria(cls, valor: str) -> str:
        if isinstance(valor, str):
            valor_limpio = valor.lower().strip()
            if valor_limpio in CATEGORIES:
                return valor_limpio
        raise ValueError(
            f"Esta categoría no existe. Categorías válidas: {CATEGORIES}"
        )


class ProductCreate(ProductBase):
    pass


class Product(ProductBase, table=True):
    __tablename__ = "app_inv_products"

    id: int | None = Field(default=None, primary_key=True)


class ProductResponse(ProductBase):
    id: int
