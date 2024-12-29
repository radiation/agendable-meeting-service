from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Exception raised for missing resources."""

    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class ValidationError(Exception):
    """Exception raised for validation errors."""

    def __init__(self, detail: str = "Validation error"):
        self.detail = detail


class ForbiddenError(Exception):
    """Exception raised for unauthorized access."""

    def __init__(self, detail: str = "Access forbidden"):
        self.detail = detail


async def forbidden_exception_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.detail},
    )


async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
