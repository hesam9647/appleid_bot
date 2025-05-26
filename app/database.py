from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    balance = Column(Float, default=0.0)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AppleID(Base):
    __tablename__ = 'apple_ids'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    price = Column(Float)
    is_sold = Column(Boolean, default=False)
    sold_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    type = Column(String)  # 'deposit', 'purchase', 'withdrawal'
    created_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subject = Column(String)
    status = Column(String)  # 'open', 'in_progress', 'answered', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

class Price(Base):
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscountCode(Base):
    __tablename__ = 'discount_codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    discount_type = Column(String)  # 'percentage' or 'fixed'
    discount_value = Column(Float)
    max_uses = Column(Integer)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscountUsage(Base):
    __tablename__ = 'discount_usages'
    
    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey('discount_codes.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    used_at = Column(DateTime, default=datetime.utcnow)

class BotSettings(Base):
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(String)
    description = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotText(Base):
    __tablename__ = 'bot_texts'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    text = Column(String)
    description = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)
    count = Column(Integer, default=1)
    reset_at = Column(DateTime)
