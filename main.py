"""
Cartly API - FastAPI entry point
run dev server ด้วย: uvicorn app.main:app --reload
Swagger UI (เอกสาร API อัตโนมัติ) จะอยู่ที่ http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.exceptions import register_exception_handlers
from database import Base, engine
from routers import auth, users, categories, products, cart, addresses, orders, reviews, uploads

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CartLy API",
    description="REST API สำหรับ Cartly Android Application",
    version="1.0.0"
)

# CORS - อนุญาตให้เรียกจาก client ใดก็ได้ (ปรับให้เฉพาะเจาะจงมากขึ้นตอน production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(addresses.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(uploads.router)

# เสิร์ฟรูปที่อัปโหลดไว้ที่ /uploads/<ชื่อไฟล์> (สาธารณะ — ชื่อไฟล์สุ่ม เดาไม่ได้)
app.mount("/uploads", StaticFiles(directory=uploads.UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {
        "message": "Cartly API is running. Visit /docs for Swagger UI."
    }
