from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
session_maker = None

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    blocked = Column(Integer, default=0)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)

async def create_db(url):
    global session_maker
    engine = create_async_engine(url)
    session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_stats():
    async with session_maker() as session:
        users = await session.execute("SELECT COUNT(*) FROM users")
        sales = await session.execute("SELECT COUNT(*) FROM products")
        txs = 0
        return users.scalar(), sales.scalar(), txs

async def add_product(name, price):
    async with session_maker() as session:
        session.add(Product(name=name, price=price))
        await session.commit()

async def get_products():
    async with session_maker() as session:
        result = await session.execute("SELECT * FROM products")
        return result.fetchall()

async def block_user(user_id):
    async with session_maker() as session:
        await session.execute(f"INSERT OR REPLACE INTO users (id, blocked) VALUES ({user_id}, 1)")
        await session.commit()

async def unblock_user(user_id):
    async with session_maker() as session:
        await session.execute(f"UPDATE users SET blocked = 0 WHERE id = {user_id}")
        await session.commit()