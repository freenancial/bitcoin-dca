import getpass

import base64
import os
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class Secret:
    @staticmethod
    def generateEncryptionKey(password_provided, salt_b64_str):
        password = password_provided.encode()
        salt = base64.b64decode(salt_b64_str.encode())
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    @staticmethod
    def encrypt(encrypt_key, content):
        return Fernet(encrypt_key).encrypt(content.encode()).decode("utf-8")

    @staticmethod
    def decrypt(encrypt_key, encrypted_content):
        return Fernet(encrypt_key).decrypt(encrypted_content.encode()).decode("utf-8")

    @staticmethod
    def encryptAllSecrets():
        while True:
            encryption_pass = getpass.getpass("Please create a password for secrets: ")
            confirm_encryption_pass = getpass.getpass("Please confirm the password: ")
            if encryption_pass != confirm_encryption_pass:
                print("Passwords doesn't match. Please try again.")
            else:
                print()
                break

        api_key = getpass.getpass("Your Coinbase Pro API key: ")
        api_secret = getpass.getpass("Your Coinbase Pro API secret: ")
        passphrase = getpass.getpass("Your Coinbase Pro API passphrase: ")
        gmail_password = getpass.getpass("Gmail user password: ")
        print()

        # Encrypt and save these secrets to `bitcoin_dca.secrets`
        salt_b64_str = base64.b64encode(os.urandom(16)).decode()
        key = Secret.generateEncryptionKey(encryption_pass, salt_b64_str)

        with open("bitcoin_dca.secrets", "w") as f:
            f.write(salt_b64_str + "\n")
            f.write(Secret.encrypt(key, api_key) + "\n")
            f.write(Secret.encrypt(key, api_secret) + "\n")
            f.write(Secret.encrypt(key, passphrase) + "\n")
            f.write(Secret.encrypt(key, gmail_password) + "\n")
            f.close()

    @staticmethod
    def decryptAllSecrets():
        encryption_pass = getpass.getpass("Password for secrets: ")
        with open("bitcoin_dca.secrets", "r") as f:
            salt_b64_str = f.readline()
            key = Secret.generateEncryptionKey(encryption_pass, salt_b64_str)
            try:
                api_key = Secret.decrypt(key, f.readline())
                api_secret = Secret.decrypt(key, f.readline())
                passphrase = Secret.decrypt(key, f.readline())
                gmail_password = Secret.decrypt(key, f.readline())
                return (api_key, api_secret, passphrase, gmail_password)
            except cryptography.fernet.InvalidToken:
                print("Password incorrect!")
                return None
