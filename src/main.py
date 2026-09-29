import os
import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, File
from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, select
from src.models.product_model import Product, ProductCreate, ProductResponse
from src.shared.database.session_db import SessionDep, engine

# Creación automática de tablas al iniciar la aplicación en PostgreSQL
SQLModel.metadata.create_all(engine)


# Config de s3 a partir del .env
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# El cliente se autentica solo gracias al rol de IAM de la EC2
s3_client = boto3.client("s3", region_name=AWS_REGION)

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

#3 subir imagen de un producto a S3
@app.post(
    "/productos/{id}/imagen",
    response_model=ProductResponse,
    summary="Subir y asociar imagen a un producto en S3"
)
async def upload_product_image(
    id: int,
    session: SessionDep,
    file: UploadFile = File(...)
):
    # 1. Validar existencia del producto
    product = session.get(Product, id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id} no encontrado."
        )

    # 2. Validar formato de imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo enviado no es una imagen válida (debe ser JPG, PNG, etc.)."
        )

    # 3. Generar un nombre único para evitar sobreescritura en S3
    extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    nombre_archivo_s3 = f"productos/{id}_{uuid.uuid4().hex[:8]}.{extension}"

    # 4. Subir archivo a Amazon S3
    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            nombre_archivo_s3,
            ExtraArgs={"ContentType": file.content_type}
        )
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir imagen a S3: {str(e)}"
        )

    # 5. Construir la URL del objeto y guardarla en Postgres
    url_imagen = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{nombre_archivo_s3}"
    product.image_url = url_imagen
    session.add(product)
    session.commit()
    session.refresh(product)

    return product


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