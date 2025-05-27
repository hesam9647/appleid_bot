from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

class ReportService:
    def __init__(self, session: Session):
        self.session = session

    async def generate_sales_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        # Get sales data
        result = await self.session.execute(
            select(
                func.date(Transaction.created_at),
                func.count(Transaction.id),
                func.sum(Transaction.amount)
            )
            .where(
                Transaction.type == 'purchase',
                Transaction.created_at.between(start_date, end_date)
            )
            .group_by(func.date(Transaction.created_at))
        )
        sales_data = result.all()
        
        # Convert to DataFrame
        df = pd.DataFrame(sales_data, columns=['date', 'count', 'amount'])
        
        # Generate charts
        plt.figure(figsize=(10, 5))
        plt.plot(df['date'], df['amount'])
        plt.title('نمودار فروش روزانه')
        
        chart_buf = io.BytesIO()
        plt.savefig(chart_buf, format='png')
        chart_buf.seek(0)
        
        return {
            'total_sales': df['amount'].sum(),
            'total_count': df['count'].sum(),
            'average_daily': df['amount'].mean(),
            'chart': chart_buf,
            'data': df.to_dict('records')
        }

    async def generate_product_report(self) -> Dict:
        # Get product sales
        result = await self.session.execute(
            select(
                Product.name,
                func.count(Transaction.id),
                func.sum(Transaction.amount)
            )
            .join(Transaction)
            .group_by(Product.id)
            .order_by(func.sum(Transaction.amount).desc())
        )
        product_data = result.all()
        
        return {
            'products': product_data,
            'total_products': len(product_data)
        }

    async def export_to_excel(self, data: Dict, filename: str) -> str:
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        # Sales sheet
        df_sales = pd.DataFrame(data['sales_data'])
        df_sales.to_excel(writer, sheet_name='Sales', index=False)
        
        # Products sheet
        df_products = pd.DataFrame(data['product_data'])
        df_products.to_excel(writer, sheet_name='Products', index=False)
        
        writer.save()
        return filename
