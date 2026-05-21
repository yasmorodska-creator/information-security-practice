from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"Згенерований ключ Fernet:")
print(f"ENCRYPTION_KEY={key.decode()}\n")
print("Цей ключ — єдиний спосіб розшифрувати дані.")
print("Втрата ключа = втрата всіх зашифрованих даних.")