from .admin import admin_router
from .user import user_router
from .error import error_router
from .user.payment import payment_router
from .user.products import products_router
from .user.payment import router as payment_router
__all__ = [
    'admin_router',
    'user_router',
    'error_router',
    'product_router'
]
