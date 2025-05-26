import pandas as pd
from typing import List, Dict

class ExcelReader:
    @staticmethod
    def validate_excel_structure(file_path: str) -> tuple[bool, str]:
        try:
            df = pd.read_excel(file_path)
            required_columns = ['email', 'password']
            
            for col in required_columns:
                if col not in df.columns:
                    return False, f"ستون {col} در فایل یافت نشد"
            
            if df.empty:
                return False, "فایل خالی است"
                
            return True, "ساختار فایل صحیح است"
        except Exception as e:
            return False, f"خطا در خواندن فایل: {str(e)}"

    @staticmethod
    def read_apple_ids(file_path: str) -> List[Dict[str, str]]:
        df = pd.read_excel(file_path)
        return df[['email', 'password']].to_dict('records')
