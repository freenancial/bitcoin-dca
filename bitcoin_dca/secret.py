import base64
import getpass
import os

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from logger import Logger

SECRET_VERSION = "1.1"


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

        # Init secrets with random strings
        api_key = base64.b64encode(os.urandom(16)).decode("utf-8")
        api_secret = base64.b64encode(os.urandom(16)).decode("utf-8")
        passphrase = base64.b64encode(os.urandom(16)).decode("utf-8")
        master_public_key = base64.b64encode(os.urandom(16)).decode("utf-8")
        gmail_password = base64.b64encode(os.urandom(16)).decode("utf-8")
        robinhood_user = base64.b64encode(os.urandom(16)).decode("utf-8")
        robinhood_password = base64.b64encode(os.urandom(16)).decode("utf-8")
        robinhood_totp = base64.b64encode(os.urandom(16)).decode("utf-8")

        if Secret.answeredYes("DCA with Coinbase Pro? (y/n): "):
            passphrase = getpass.getpass("Your Coinbase Pro API passphrase: ")
            api_secret = getpass.getpass("Your Coinbase Pro API secret: ")
            api_key = getpass.getpass("Your Coinbase Pro API key: ")
            print("")

            if Secret.answeredYes("Auto withdraw Bitcoin? (y/n): "):
                master_public_key = getpass.getpass("Master public key: ")
                print("")

                if Secret.answeredYes("Send out email notifications? (y/n): "):
                    gmail_password = getpass.getpass("Gmail user password: ")
                    print("")

        if Secret.answeredYes("DCA with Robinhood? (y/n): "):
            robinhood_user = getpass.getpass("Your Robinhood username: ")
            robinhood_password = getpass.getpass("Your Robinhood password: ")
            robinhood_totp = getpass.getpass("Your Robinhood TOTP: ")

        print()

        # Encrypt and save these secrets to `bitcoin_dca.secrets`
        salt_b64_str = base64.b64encode(os.urandom(16)).decode()
        key = Secret.generateEncryptionKey(encryption_pass, salt_b64_str)

        with open("bitcoin_dca.secrets", "w") as f:
            f.write(SECRET_VERSION + "\n")
            f.write(salt_b64_str + "\n")
            f.write(Secret.encrypt(key, api_key) + "\n")
            f.write(Secret.encrypt(key, api_secret) + "\n")
            f.write(Secret.encrypt(key, passphrase) + "\n")
            f.write(Secret.encrypt(key, master_public_key) + "\n")
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
            secret_version = f.readline().strip()
            if secret_version != SECRET_VERSION:
                Logger.error(
                    f"Wrong secret version. Expected: '{SECRET_VERSION}'; Found: '{secret_version}'"
                )
                raise Exception(
                    "Secret version mismatch. Please create a new secret valut by `make update_secrets`"
                )
            salt_b64_str = f.readline()
            key = Secret.generateEncryptionKey(encryption_pass, salt_b64_str)
            try:
                api_key = Secret.decrypt(key, f.readline()).strip()
                api_secret = Secret.decrypt(key, f.readline()).strip()
                passphrase = Secret.decrypt(key, f.readline()).strip()
                master_public_key = Secret.decrypt(key, f.readline()).strip()
                gmail_password = Secret.decrypt(key, f.readline()).strip()
                robinhood_user = Secret.decrypt(key, f.readline()).strip()
                robinhood_password = Secret.decrypt(key, f.readline()).strip()
                robinhood_totp = Secret.decrypt(key, f.readline()).strip()
                Secret.secrets_dict = {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "passphrase": passphrase,
                    "master_public_key": master_public_key,
                    "gmail_password": gmail_password,
                    "robinhood_user": robinhood_user,
                    "robinhood_password": robinhood_password,
                    "robinhood_totp": robinhood_totp,
                }
                return Secret.secrets_dict
            except cryptography.fernet.InvalidToken:
                Logger.critical("Invalid encryption_pass, unable to unlock secrets!")
                raise
