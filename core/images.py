"""
ตรวจชนิดไฟล์รูปจาก "ไบต์แรกของไฟล์" (magic bytes) - ไม่เชื่อชือไฟล์หรือ Content-Type ที่ client ส่งมา
แยกเป็นฟังก์ชันล้วนๆ (ไม่พึ่ง FastAPI) เพื่อให้ทดสอบง่าย
"""
from typing import Optional

def detect_image_ext(head: bytes) -> Optional[str]:
    """คืนนามสกุลไฟล์ (".jpg", ".png", ".webp") ถ้าเป้นรูปที่รองรับ ไม่งั้นคืน None"""
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    return None
