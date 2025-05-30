# app/keyboards/__init__.py

from app.keyboards.admin_kb import (
    admin_main_menu_kb,
    admin_users_kb,
    admin_user_actions_kb,
    admin_products_kb,
    admin_settings_kb,
    admin_stats_kb,
    admin_broadcast_kb
)

from app.keyboards.user_kb import (
    main_menu_kb,
    wallet_kb,
    profile_kb,
    support_kb,
    purchase_history_kb,
    payment_kb,
    product_kb,
    order_kb
)

__all__ = [
    # Admin keyboards
    'admin_main_menu_kb',
    'admin_users_kb',
    'admin_user_actions_kb',
    'admin_products_kb',
    'admin_settings_kb',
    'admin_stats_kb',
    'admin_broadcast_kb',
    
    # User keyboards
    'main_menu_kb',
    'wallet_kb',
    'profile_kb',
    'support_kb',
    'purchase_history_kb',
    'payment_kb',
    'product_kb',
    'order_kb'
]
