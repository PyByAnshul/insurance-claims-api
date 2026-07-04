from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, error: str, message: str, status_code: int = 400):
        self.error = error
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    def __init__(self, message: str):
        super().__init__("NotFound", message, 404)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__("Conflict", message, 409)


class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__("ValidationError", message, 422)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "An unexpected error occurred"},
    )
