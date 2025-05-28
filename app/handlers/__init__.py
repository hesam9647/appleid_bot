from .admin import admin_router
from .user import user_router


__all__ = [
    'admin_router',
    'user_router',
    'error_router',
    'payment_router',
    'product_router'
]
