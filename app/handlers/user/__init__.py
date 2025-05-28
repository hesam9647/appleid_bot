from aiogram import Router
from .start import router as start_router
from .orders import router as orders_router
from .products import router as products_router
from .profile import router as profile_router
from .payment import router as payment_router

# Create user router
user_router = Router()

# Include all user routers
user_router.include_router(start_router)
user_router.include_router(orders_router)
user_router.include_router(products_router)
user_router.include_router(profile_router)
user_router.include_router(payment_router)
