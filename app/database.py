from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from datetime import datetime

class Base(DeclarativeBase):
    pass

# ---------------------- User System ----------------------
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, index=True)
    balance = Column(Float, default=0.0)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

# ---------------------- AppleID System ----------------------
class AppleID(Base):
    __tablename__ = 'apple_ids'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    price = Column(Float)
    is_sold = Column(Boolean, default=False, index=True)
    sold_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sold_at = Column(DateTime, nullable=True)

# ---------------------- Transaction System ----------------------
class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    amount = Column(Float)
    type = Column(String, index=True)  # 'deposit', 'purchase', 'withdrawal'
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

# ---------------------- Ticket System ----------------------
class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    title = Column(String)
    status = Column(String, default='open', index=True)
    priority = Column(String, default='normal', index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(Base):
    __tablename__ = 'ticket_messages'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), index=True)
    sender_id = Column(Integer, ForeignKey('users.id'), index=True)
    message_type = Column(String, default='text')
    content = Column(String)
    file_id = Column(String, nullable=True)
    is_from_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="messages")
    sender = relationship("User")

# ---------------------- Discount System ----------------------
class DiscountCode(Base):
    __tablename__ = 'discount_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    discount_type = Column(String)  # 'percentage' or 'fixed'
    discount_value = Column(Float)
    max_uses = Column(Integer)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    usages = relationship("DiscountUsage", cascade="all, delete-orphan")

class DiscountUsage(Base):
    __tablename__ = 'discount_usages'

    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey('discount_codes.id'), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    used_at = Column(DateTime, default=datetime.utcnow)

    discount = relationship("DiscountCode")
    user = relationship("User")

# ---------------------- Bot Settings System ----------------------
class BotSettings(Base):
    __tablename__ = 'bot_settings'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotText(Base):
    __tablename__ = 'bot_texts'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    text = Column(String)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------------------- Rate Limit System ----------------------
class RateLimit(Base):
    __tablename__ = 'rate_limits'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    action = Column(String, index=True)
    count = Column(Integer, default=1)
    reset_at = Column(DateTime, index=True)

# ---------------------- Product System ----------------------
class ProductCategory(Base):
    __tablename__ = 'product_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey('product_categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
    subcategories = relationship("ProductCategory", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String)
    base_price = Column(Float)
    stock = Column(Integer, default=0)
    stock_alert_threshold = Column(Integer, default=5)
    last_stock_update = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    category_id = Column(Integer, ForeignKey('product_categories.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("ProductCategory", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    prices = relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")

class ProductPrice(Base):
    __tablename__ = 'product_prices'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), index=True)
    price = Column(Float)
    type = Column(String, index=True)  # 'discount', 'special', etc.
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="prices")

# ---------------------- Order System ----------------------
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    total_amount = Column(Float)
    status = Column(String, index=True)  # pending, paid, completed, cancelled
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=True)
    discount_id = Column(Integer, ForeignKey('discount_codes.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment")
    discount = relationship("DiscountCode")

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), index=True)
    product_id = Column(Integer, ForeignKey('products.id'), index=True)
    quantity = Column(Integer)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

# ---------------------- Payment System ----------------------
class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    method = Column(String, index=True)
    status = Column(String, index=True)
    amount = Column(Float)
    transaction_id = Column(String, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    order = relationship("Order", back_populates="payment")

# ---------------------- Notification System ----------------------
class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    title = Column(String)
    message = Column(String)
    type = Column(String, index=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

# ---------------------- Database Initialization ----------------------
async def init_db(database_url: str):
    """Initialize the database with async support"""
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    return async_session


# Context manager for database sessions
async def get_session():
    """Async context manager for database sessions"""
    async with async_sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()
