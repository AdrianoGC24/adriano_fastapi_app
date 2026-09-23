from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from src.models.product_model import Product
from src.shared.database.session_db import SessionDep, get_session

app = FastAPI()


@app.post("/product")
def create_product(product: Product, session: SessionDep):
    producto_existente = session.exec(
        select(Product).where(Product.name == product.name)
    ).first()
    
    if producto_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto registrado con el nombre '{product.name}'."
        )
        
    
    session.add(product)
    session.commit()
    session.refresh(product)

    return product

@app.get("/product")
def get_products(session: SessionDep):
    products = session.exec(
        select(Product)
    ).all()

    return products

@app.delete('/product/{product_id}')
def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Producto con ID {product_id} no encontrado.',
        )

    session.delete(product)
    session.commit()
    return {'mensaje': 'Producto eliminado correctamente'}