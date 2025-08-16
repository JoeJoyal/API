from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field as PyField
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint
from sqlmodel import Session
import secrets

app = FastAPI(title="Order & Inventory Micro-service")

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"

class Product(BaseModel):
    id: Optional[int] = None
    sku: str
    product_name: str
    brand_id: int
    category_id: int
    stock: int = PyField(gt=0)
    price: float = PyField(gt=0)

class Order(BaseModel):
    id: Optional[int] = None
    product_id: int
    quantity: int = PyField(gt=0)
    total: float = 0.0
    order_status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = PyField(default_factory=datetime.utcnow)
    customer_id: int

class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: str # In production: hash only:

class LoginRequest(BaseModel):
    username: str
    password: str

_products: Dict[int, Product] = {}
_next_product_id = 1

_orders: Dict[int, Order] = {}
_next_order_id = 1

_users: Dict[int, User] = {}
_next_user_id = 1

_api_keys: Dict[int, str] = {} # user_id --> api_key

# 1. Welcome greeting
@app.get("/greeting/")
def welcome():
    return {"message": "Welcome to the Order & Inventory Micro-service!"}

# 2. Create a user
@app.post("/users/", response_model=User, status_code=201)
def create_user(user: User):
    global _next_user_id
    for u in _users.values():
        if u.username == user.username:
            raise HTTPException(409, detail="Username already exists")
        if u.email == user.email:
            raise HTTPException(409, detail="Email already exists")
    user.id = _next_user_id
    _users[_next_user_id] = user
    _next_user_id +=1
    return user

# 3. User login
@app.post("/user/login/")
def user_login(credentials: LoginRequest):
    for user in _users.values():
        if user.username == credentials.username and user.password == credentials.password:
            return {"message": "Login successful", "user_id": user.id}
    raise HTTPException(401, detail="Invalid credentails")

# 4. Create an API Key (GET)
@app.get("/apikeys/create/")
def create_apikey(user_id: int):
    if user_id not in _users:
        raise HTTPException(404, detail="User not found")
    api_key = secrets.token_hex(16)
    _api_keys[user_id] = api_key
    return {"user_id": user_id, "api_key": api_key}

# 5. Get API Key (GET)
@app.get("/apikeys/")
def get_apikey(user_id: int):
    if user_id not in _users:
        raise HTTPException(404, details="User not found")
    Key = _api_keys.get(user_id)
    if not Key:
        raise HTTPException(404, detail="API Key not found")
    return {"user_id": user_id, "api_key": Key}

# 6. Create a product
@app.post("/products/", response_model=Product, status_code=201)
def create_product(product: Product):
    global _next_product_id
    for p in _products.values():
        if p.sku == product.sku:
            raise HTTPException(status_code=409, details="Stock Keep Unit already exists")
    product.id = _next_product_id
    _products[_next_product_id] = product
    _next_product_id +=1
    return product

# 7. Products list
@app.get("/products/", response_model=List[Product])
def list_products():
    return list(_products.values())

# 8. Get product with id
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = _products.get(product_id)
    if not product:
        raise HTTPException(404, detail="Product not found")
    return product

# 9. Update product with id
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, update: Product):
    if product_id not in _products:
        raise HTTPException(404, detail="Product not found")
    # Optional: Check SKU uniqueness on update
    for pid, prod in _products.items():
        if pid != product_id and prod.sku == update.sku:
            raise HTTPException(409, detail="SKU already exists for another product")
    update.id = product_id
    _products[product_id] = update
    return update

# 10. 10. Delete product with id
@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    if product_id not in _products:
        raise HTTPException(404, detail="Product not found")
    del _products[product_id]
    return

# 11. Create order
@app.post("/orders/", response_model=Order, status_code=201)
def place_order(order: Order):
    global _next_order_id
    product = _products.get(order.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if order.quantity > product.stock:
        raise HTTPException(409, "Insufficient stock")
    product.stock -= order.quantity
    order.id = _next_order_id
    order.total = product.price * order.quantity
    order.created_at = datetime.utcnow()
    order.order_status = OrderStatus.PENDING
    _orders[_next_order_id] = order
    _next_order_id +=1
    return order

# 12. Orders list
@app.get("/orders/", response_model=List[Order])
def list_orders():
    return list(_orders.values())

# 13. Get order with id
@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(404, detail="Order not found")
    return order

# 14. Update order with id
@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, update: Order):
    if order_id not in _orders:
        raise HTTPException(404, detail="Order not found")
    existing_order = _orders[order_id]
    # Update product stock if changing quantity or product
    if update.product_id != existing_order.product_id or update.quantity != existing_order.quantity:
        # Refund stock of old product
        old_product = _products.get(existing_order.product_id)
        if old_product:
            old_product.stock += existing_order.quantity
        # Reserve stock for new product
        new_product = _products.get(update.product_id)
        if not new_product:
            raise HTTPException(404, "New product not found")
        if update.quantity > new_product.stock:
            raise HTTPException(409, "Insufficient stock for update")
        new_product.stock -= update.quantity
    update.id = order_id
    update.total = _products[update.product_id].price * update.quantity
    update.created_at = existing_order.created_at
    _orders[order_id] = update
    return update


# 15. Delete order with id
@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int):
    if order_id not in _orders:
        raise HTTPException(404, detail="Order not found")
    order = _orders[order_id]
    product = _products.get(order.product_id)
    if product:
        product.stock += order.quantity  # Refund stock
    del _orders[order_id]
    return

# 16. Webhooks payment
@app.post("/webhooks/payment")
def payment_webhook(order_id: int):
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(404, detail="Order not found")
    order.order_status = OrderStatus.PAID
    return {"ok": True}