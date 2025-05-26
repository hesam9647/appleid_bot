from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List

from app.database import User, Transaction, AppleID, Ticket

class StatsService:
    def __init__(self, session: Session):
        self.session = session

    async def get_sales_stats(self, days: int = 30) -> Dict:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Get daily sales
        result = await self.session.execute(
            select(
                func.date(Transaction.created_at),
                func.count(Transaction.id),
                func.sum(Transaction.amount)
            )
            .where(
                Transaction.type == 'purchase',
                Transaction.created_at >= date_from
            )
            .group_by(func.date(Transaction.created_at))
            .order_by(func.date(Transaction.created_at))
        )
        daily_sales = result.all()
        
        # Convert to pandas for easier analysis
        df = pd.DataFrame(daily_sales, columns=['date', 'count', 'amount'])
        
        return {
            'total_sales': int(df['amount'].sum()),
            'total_count': int(df['count'].sum()),
            'average_daily': int(df['amount'].mean()),
            'daily_data': df.to_dict('records')
        }

    async def get_user_stats(self) -> Dict:
        total_users = await self.session.scalar(select(func.count(User.id)))
        
        active_users = await self.session.scalar(
            select(func.count(User.id))
            .where(User.is_blocked == False)
        )
        
        new_users_24h = await self.session.scalar(
            select(func.count(User.id))
            .where(User.created_at >= datetime.utcnow() - timedelta(days=1))
        )
        
        users_with_purchase = await self.session.scalar(
            select(func.count(func.distinct(Transaction.user_id)))
            .where(Transaction.type == 'purchase')
        )
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'new_users_24h': new_users_24h,
            'users_with_purchase': users_with_purchase,
            'conversion_rate': round(users_with_purchase / total_users * 100, 2) if total_users > 0 else 0
        }

    async def get_inventory_stats(self) -> Dict:
        total = await self.session.scalar(select(func.count(AppleID.id)))
        available = await self.session.scalar(
            select(func.count(AppleID.id))
            .where(AppleID.is_sold == False)
        )
        sold = await self.session.scalar(
            select(func.count(AppleID.id))
            .where(AppleID.is_sold == True)
        )
        
        return {
            'total': total,
            'available': available,
            'sold': sold,
            'sold_percentage': round(sold / total * 100, 2) if total > 0 else 0
        }

    async def get_support_stats(self) -> Dict:
        total_tickets = await self.session.scalar(select(func.count(Ticket.id)))
        
        open_tickets = await self.session.scalar(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_(['open', 'in_progress']))
        )
        
        avg_response_time = await self.session.scalar(
            select(func.avg(
                func.julianday(Ticket.updated_at) - func.julianday(Ticket.created_at)
            ) * 24)
            .where(Ticket.status == 'answered')
        )
        
        return {
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'avg_response_time': round(avg_response_time, 1) if avg_response_time else 0
        }

    async def generate_excel_report(self, days: int = 30) -> str:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Get transactions
        result = await self.session.execute(
            select(
                Transaction.id,
                Transaction.user_id,
                Transaction.amount,
                Transaction.type,
                Transaction.created_at
            )
            .where(Transaction.created_at >= date_from)
            .order_by(Transaction.created_at.desc())
        )
        transactions = result.all()
        
        # Create Excel writer
        filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        # Transactions sheet
        df_trans = pd.DataFrame(transactions, columns=['id', 'user_id', 'amount', 'type', 'created_at'])
        df_trans.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Daily summary sheet
        daily_summary = df_trans.groupby([df_trans['created_at'].dt.date, 'type']).agg({
            'amount': ['sum', 'count']
        }).reset_index()
        daily_summary.to_excel(writer, sheet_name='Daily Summary', index=False)
        
        writer.save()
        return filename
