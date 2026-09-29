from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, select
from src.models.product_model import Product, ProductCreate, ProductResponse
from src.shared.database.session_db import SessionDep, engine

# Creación automática de tablas al iniciar la aplicación en PostgreSQL
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="API de Gestión de Productos",
    description="API de inventario construida con FastAPI y SQLModel",
    version="1.0.0"
)


# 1. GET /productos: Listar productos
@app.get(
    "/productos",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los productos"
)
def get_products(session: SessionDep):
    products = session.exec(select(Product)).all()
    return products


# 2. POST /productos: Crear producto
@app.post(
    "/productos",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto"
)
def create_product(product_in: ProductCreate, session: SessionDep):
    # Validar si ya existe un producto con el mismo nombre
    producto_existente = session.exec(
        select(Product).where(Product.name == product_in.name)
    ).first()

    if producto_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto registrado con el nombre '{product_in.name}'."
        )

    db_product = Product.model_validate(product_in)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


# 3. DELETE /productos/{id}: Eliminar producto por ID
@app.delete(
    "/productos/{id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un producto por su ID"
)
def delete_product(id: int, session: SessionDep):
    product = session.get(Product, id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    session.delete(product)
    session.commit()
    return {"mensaje": "Producto eliminado correctamente"}