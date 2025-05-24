# utils/security.py
from cryptography.fernet import Fernet
import os

# تولید کلید و ذخیره در فایل امن
def generate_and_save_key(filepath='keys/secret.key'):
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(key)
    return key

# بارگذاری کلید
def load_key(filepath='keys/secret.key'):
    with open(filepath, 'rb') as f:
        return f.read()

# رمزنگاری متن
def encrypt_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

# رمزگشایی متن
def decrypt_data(token: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token).decode()

# نمونه استفاده
if __name__ == "__main__":
    # برای اولین بار کلید رو تولید کن
    key_path = 'keys/secret.key'
    if not os.path.exists(key_path):
        key = generate_and_save_key(key_path)
        print("کلید ساخته شد و در مسیر keys/secret.key ذخیره شد.")
    else:
        key = load_key(key_path)
        print("کلید بارگذاری شد.")