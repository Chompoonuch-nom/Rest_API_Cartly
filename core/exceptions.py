"""
Custom exeptions + global exception handlers สำหรับ FastAPI app
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class ResourceNotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message

class BadRequestException(Exception):
    def __init__(self, message: str):
        self.message = message

def register_exception_handlers(app):

    @app.exception_handler(ResourceNotFoundException)
    async def not_found_handler(request: Request, exc: ResourceNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": exc.message, "data": None}
        )
    
    @app.exception_handler(BadRequestException)
    async def validation_handler(request: Request, exc: BadRequestException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": exc.message, "data": None}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = "; ".join(
            f"{'.'.join(str(x) for x in e['loc'])}: {e['msg']}" for e in exc.errors()
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": f"Validation failed: {errors}", "data": None},
        )
    
    @app.exception_handler(Exception)
    async def general_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_DERVER_ERROR,
            content={"success": False, "message": f"Internal server error: {str(exc)}", "data": None},
        )