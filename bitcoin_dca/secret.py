import base64
import getpass
import os

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from logger import Logger


class Secret:
    secrets_dict = None

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
    def answeredYes(prompt_text):
        answer = input(prompt_text)
        return answer.lower()[:1] == "y"

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

        # Init empty secrets
        api_key = ""
        api_secret = ""
        passphrase = ""
        gmail_password = ""
        robinhood_user = ""
        robinhood_password = ""
        robinhood_totp = ""

        if Secret.answeredYes("DCA with Coinbase Pro? (y/n): "):
            api_key = getpass.getpass("Your Coinbase Pro API key: ")
            api_secret = getpass.getpass("Your Coinbase Pro API secret: ")
            passphrase = getpass.getpass("Your Coinbase Pro API passphrase: ")

        if Secret.answeredYes("DCA with Robinhood? (y/n): "):
            robinhood_user = getpass.getpass("Your Robinhood username: ")
            robinhood_password = getpass.getpass("Your Robinhood password: ")
            robinhood_totp = getpass.getpass("Your Robinhood TOTP: ")

        if Secret.answeredYes("Send out email notifications? (y/n): "):
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
            f.write(Secret.encrypt(key, robinhood_user) + "\n")
            f.write(Secret.encrypt(key, robinhood_password) + "\n")
            f.write(Secret.encrypt(key, robinhood_totp) + "\n")
            f.close()

    @staticmethod
    def decryptAllSecrets(encryption_pass=None):
        if Secret.secrets_dict:
            return Secret.secrets_dict

        if not encryption_pass:
            encryption_pass = getpass.getpass("Password for unlocking secrets: ")
        with open("bitcoin_dca.secrets", "r") as f:
            salt_b64_str = f.readline()
            key = Secret.generateEncryptionKey(encryption_pass, salt_b64_str)
            try:
                api_key = Secret.decrypt(key, f.readline())
                api_secret = Secret.decrypt(key, f.readline())
                passphrase = Secret.decrypt(key, f.readline())
                gmail_password = Secret.decrypt(key, f.readline())
                robinhood_user = Secret.decrypt(key, f.readline())
                robinhood_password = Secret.decrypt(key, f.readline())
                robinhood_totp = Secret.decrypt(key, f.readline())
                Secret.secrets_dict = {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "passphrase": passphrase,
                    "gmail_password": gmail_password,
                    "robinhood_user": robinhood_user,
                    "robinhood_password": robinhood_password,
                    "robinhood_totp": robinhood_totp,
                }
                return Secret.secrets_dict
            except cryptography.fernet.InvalidToken:
                Logger.critical("Invalid encryption_pass, unable to unlock secrets!")
                raise
