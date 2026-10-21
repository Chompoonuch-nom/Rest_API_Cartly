"""
อัปโหลดรูปภาพ (สินค้า / ไอคอนหมวดหมู่ / รูปโปรไฟล์) — เก็บไฟล์ลงดิสก์ แล้วให้ client เอา url ไปใช้กับ endpoint อื่น

POST /api/uploads/images   (multipart/form-data, field ชื่อ "file", ต้อง login)
  -> { "success": true, "data": { "url": "/uploads/<ชื่อสุ่ม>.jpg" } }
ไฟล์ถูกเสิร์ฟสาธารณะที่ GET /uploads/<ชื่อไฟล์> (ดู app/main.py)
"""
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from config import settings
from core.deps import get_current_user
from core.exceptions import BadRequestException
from core.images import detect_image_ext
from models.models import User
from schemas.schemas import UploadOut, ApiResponse

# โฟลเดอร์เก็บรูป = <root โปรเจกต์>/uploads (ไม่ขึ้นกับว่ารัน uvicorn จากโฟลเดอร์ไหน)
UPLOAD_DIR = Path(__file__).resolve().parents[2] / settings.upload_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api/uploads", tags=["Upload"])


@router.post("/images", response_model=ApiResponse[UploadOut])
def upload_image(file: UploadFile = File(...), _current_user: User = Depends(get_current_user)):
    max_bytes = settings.max_upload_mb * 1024 * 1024

    data = file.file.read(max_bytes + 1)  # อ่านเกินขีดจำกัด 1 ไบต์ไว้เช็คว่าใหญ่เกินไหม
    if not data:
        raise BadRequestException("ไฟล์ว่างเปล่า")
    if len(data) > max_bytes:
        raise BadRequestException(f"ไฟล์ใหญ่เกิน {settings.max_upload_mb} MB")

    ext = detect_image_ext(data[:12])
    if ext is None:
        raise BadRequestException("รองรับเฉพาะรูปภาพ JPEG, PNG หรือ WEBP")

    # ตั้งชื่อใหม่เองทั้งหมด (สุ่ม) — ไม่ใช้ชื่อจาก client เพื่อกัน path traversal / ชื่อซ้ำ
    filename = f"{secrets.token_hex(16)}{ext}"
    (UPLOAD_DIR / filename).write_bytes(data)

    return ApiResponse(message="อัปโหลดรูปภาพสำเร็จ", data=UploadOut(url=f"/uploads/{filename}"))
