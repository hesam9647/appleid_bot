import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()  # ایجاد کلاس پایه برای مدل‌ها

async def create_db(database_url):
    # ساخت ارتباط با دیتابیس به صورت غیر همزمان
    engine = create_async_engine(database_url, echo=True)

    # ساخت جلسه به صورت غیر همزمان
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # ایجاد جداول برای تمامی مدل‌ها
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # اتصال به دیتابیس و انجام عملیات در صورت نیاز
    async with async_session() as session:
        async with session.begin():
            pass  # می‌توانید عملیات دیتابیس خود را در اینجا انجام دهید

    print("✅ دیتابیس به درستی ایجاد شد.")
