from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# تفعيل الـ CORS بشكل صحيح ليقبل الطلبات القادمة من الـ Live Server (بورت 5500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# قواعد البيانات المؤقتة
products_db = []
orders_db = []
users_db = []

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    category: str
    img: str  # الـ img هنا هتقبل نص الـ Base64 الطويل الخاص بالصورة بدون مشاكل

class Order(BaseModel):
    order_id: Optional[str] = None
    items: List[str] = []
    total_price: float
    phone: str
    status: str = "قيد الانتظار"

class UserRegister(BaseModel):
    name: str
    phone: str
    password: str

class OtpVerify(BaseModel):
    phone: str
    otp_code: str

# === 🛍️ مسارات المنتجات ===
@app.get("/api/products")
def get_products():
    return products_db

@app.post("/api/products")
def add_product(product: Product):
    product.id = len(products_db) + 1
    products_db.append(product)
    return {"message": "تمت إضافة المنتج بنجاح!", "product": product}

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    global products_db
    products_db = [p for p in products_db if p.id != product_id]
    return {"message": f"تم حذف المنتج رقم {product_id} بنجاح"}

# === 📦 مسارات الطلبات ===
@app.post("/api/orders")
def create_order(order: Order):
    order.order_id = f"TRND-{len(orders_db) + 101}"
    orders_db.append(order)
    return {"message": "تم حجز طلبك بنجاح!", "order": order}

@app.get("/api/admin/orders")
def get_admin_orders():
    return {"orders": orders_db}

# === 👥 مسارات الحسابات والـ OTP ===
@app.post("/api/register")
def register_user(user: UserRegister):
    dev_otp = "1234"
    users_db.append({
        "name": user.name,
        "phone": user.phone,
        "password": user.password,
        "verified": False,
        "otp": dev_otp
    })
    return {"message": "تم التسجيل مبدئياً، يرجى التحقق", "dev_mode_otp": dev_otp}

@app.post("/api/verify-otp")
def verify_otp(otp_data: OtpVerify):
    for u in users_db:
        if u["phone"] == otp_data.phone and u["otp"] == otp_data.otp_code:
            u["verified"] = True
            return {"message": "تم تفعيل الحساب بنجاح!"}
    raise HTTPException(status_code=400, detail="كود التحقق غير صحيح أو الهاتف غير مسجل")