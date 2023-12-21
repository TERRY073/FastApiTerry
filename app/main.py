#Trabajo realizado en conjunto con Jose David y Juan Camilo valencia

import os
from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static"), name="static")


# Models
class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool


class User(BaseModel):
    id: int
    name: str
    email: str


class Order(BaseModel):
    id: int
    user_id: int
    products: List[Product]
    total_price: float


# Datos
products = [
    Product(id=1, name="Halo 4", price=14500, in_stock=True),
    Product(id=2, name="Halo Infinite", price=4500, in_stock=True),
]

users = [
    User(id=1, name="Terry", email="terry40733@gmail.com"),
]

orders = []


# Rutas
@app.get("/api")
async def read_root():
    return {"Hello": "Terry"}


@app.get("/favicon.ico")
async def favicon():
    file_name = "favicon.ico"
    file_path = f"./app/static/{file_name}"
    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


# Products CRUD
@app.get("/products", tags=["Products"])
def get_products():
    return products


@app.post("/products", tags=["Products"])
def add_product(product: Product):
    if any(p.id == product.id for p in products):
        raise HTTPException(status_code=400, detail="El Producto ya existe")

    products.append(product)
    return product


@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: int, product: Product):
    for idx, p in enumerate(products):
        if p.id == product_id:
            products[idx] = product
            return product
    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: int):
    for idx, p in enumerate(products):
        if p.id == product_id:
            del products[idx]
            return {"message": "Producto eliminado"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# Users CRUD
@app.post("/users", tags=["Users"])
def create_user(user: User):
    users.append(user)
    return user


@app.put("/users/{user_id}", tags=["Users"])
def update_user(user_id: int, user: User):
    for idx, u in enumerate(users):
        if u.id == user_id:
            users[idx] = user
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int):
    for idx, u in enumerate(users):
        if u.id == user_id:
            del users[idx]
            return {"message": "Usuario eliminado"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Orders CRUD
@app.get("/orders", tags=["Orders"])
def get_orders():
    return orders


@app.post("/orders", tags=["Orders"])
def create_order(order: Order):
    try:
        _ = next(u for u in users if u.id == order.user_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for product in order.products:
        try:
            _ = next(p for p in products if p.id == product.id and p.in_stock)
        except StopIteration:
            raise HTTPException(
                status_code=400,
                detail=f"Producto {product.id} no encontrado o no está en stock",
            )

    new_order = Order(
        id=order.id,
        user_id=order.user_id,
        products=order.products,
        total_price=sum(p.price for p in order.products),
    )
    orders.append(new_order)
    return {"message": "Orden creada"}


@app.put("/orders/{order_id}", tags=["Orders"])
def update_order(order_id: int, order: Order):
    try:
        _ = next(o for o in orders if o.id == order_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    for idx, o in enumerate(orders):
        if o.id == order_id:
            orders[idx] = order
            return {"message": "Orden actualizada"}

    raise HTTPException(status_code=500, detail="Error interno")


@app.delete("/orders/{order_id}", tags=["Orders"])
def delete_order(order_id: int):
    try:
        _ = next(o for o in orders if o.id == order_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    for idx, o in enumerate(orders):
        if o.id == order_id:
            del orders[idx]
            return {"message": "Orden eliminada"}

    raise HTTPException(status_code=500, detail="Error interno")
