import os
import json
import hashlib
import random
import string
import base64
from cryptography.fernet import Fernet
from getpass import getpass

DATA_FILE = "passwords_encrypted.dat"

def derive_key(password: str) -> bytes:
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_and_save(data, key):
    f = Fernet(key)
    encrypted = f.encrypt(json.dumps(data).encode())
    with open(DATA_FILE, "wb") as file:
        file.write(encrypted)

def load_and_decrypt(key):
    if not os.path.exists(DATA_FILE):
        return {}
    f = Fernet(key)
    try:
        with open(DATA_FILE, "rb") as file:
            encrypted = file.read()
        decrypted = f.decrypt(encrypted).decode()
        return json.loads(decrypted)
    except Exception:
        print("❌ Incorrect master password or corrupted data.")
        exit()

def ask_yes_no(prompt):
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ["y", "yes"]:
            return True
        elif ans in ["n", "no"]:
            return False
        else:
            print("Please type 'y' or 'n'.")

def ask_password_length():
    while True:
        try:
            num = int(input("🔢 How many characters should the password be? (Min: 8): ").strip())
            if num >= 8:
                return num
            print("Must be at least 8.")
        except ValueError:
            print("Please enter a valid number.")

def generate_password(base, use_special, length):
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed = hashlib.sha256((base + salt).encode()).hexdigest()
    characters = string.ascii_letters + string.digits
    if use_special:
        characters += ".!^+%&/"
    return ''.join(random.choices(characters + hashed, k=length))

def create_new_password(data):
    user_input = input("✍️ Enter a word or sentence: ").strip()
    if user_input in data:
        print(f"⚠️ A password already exists for '{user_input}': {data[user_input]}")
        return data

    use_special = ask_yes_no("Do you want special characters (e.g. .!^+%&/)?")
    length = ask_password_length()
    new_pass = generate_password(user_input, use_special, length)
    data[user_input] = new_pass
    print(f"✅ New strong password saved: {new_pass}")
    return data

def delete_password(data):
    if not data:
        print("📂 No saved passwords to delete.")
        return data

    print("\n📜 Stored phrases:")
    for i, key in enumerate(data.keys(), 1):
        print(f"  {i}. {key}")

    target = input("\n🗑️ Type the exact word/sentence you want to delete: ").strip()
    if target not in data:
        print("❌ Entry not found.")
        return data

    confirm = input(f"⚠️ Are you sure you want to delete '{target}'? (y/n): ").strip().lower()
    if confirm == 'y':
        del data[target]
        print(f"✅ '{target}' and its password deleted.")
    else:
        print("❎ Deletion canceled.")
    return data

def edit_password(data):
    if not data:
        print("❗ No stored passwords to edit.")
        return data

    print("📜 Stored phrases:")
    for i, key in enumerate(data.keys(), 1):
        print(f"  {i}. {key}")

    target = input("\n✏️ Type the exact word/sentence you want to edit: ").strip()
    if target not in data:
        print("❌ Entry not found.")
        return data

    use_special = ask_yes_no("Do you want special characters in the new password?")
    length = ask_password_length()
    updated_password = generate_password(target, use_special, length)
    data[target] = updated_password
    print(f"✅ Password for '{target}' updated: {updated_password}")
    return data

def show_passwords(data):
    if not data:
        print("📂 No saved passwords.")
    else:
        print("\n📂 Stored passwords:")
        for k, v in data.items():
            print(f"- '{k}' ➜ {v}")

def main():
    print("🔐 Secure Password Generator with Encrypted Storage")

    master_password = getpass("🔑 Enter your master password: ")
    key = derive_key(master_password)

    data = load_and_decrypt(key)

    show_passwords(data)

    while True:
        print("\n➡️ What would you like to do?")
        print("  [c] Create new password")
        print("  [d] Delete saved password")
        print("  [e] Edit existing password")
        print("  [s] Show saved passwords")
        print("  [x] Exit")

        choice = input("➤ Choose (c/d/e/s/x): ").strip().lower()

        if choice == 'c':
            data = create_new_password(data)
            encrypt_and_save(data, key)
        elif choice == 'd':
            data = delete_password(data)
            encrypt_and_save(data, key)
        elif choice == 'e':
            data = edit_password(data)
            encrypt_and_save(data, key)
        elif choice == 's':
            show_passwords(data)
        elif choice == 'x':
            print("👋 Exiting. Goodbye!")
            break
        else:
            print("❗ Invalid option. Please choose 'c', 'd', 'e', 's', or 'x'.")

if __name__ == "__main__":
    main()
