# utils/zip_encrypt.py
import zipfile
import os

def create_password_protected_zip(file_path, zip_name, password):
    with zipfile.ZipFile(zip_name, 'w') as zf:
        zf.setpassword(password.encode())
        zf.write(file_path, arcname=os.path.basename(file_path))
    print(f"فایل ZIP با نام {zip_name} ساخته شد.")

# نمونه استفاده
if __name__ == "__main__":
    create_password_protected_zip('payment_receipt.txt', 'receipt.zip', 'your_password123')