import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")
    ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
    ENV = os.getenv("OANDA_ENV", "practice")

    @classmethod
    def validate(cls):
        if not cls.ACCESS_TOKEN:
            raise ValueError("OANDA_ACCESS_TOKEN is not set")
        if not cls.ACCOUNT_ID:
            raise ValueError("OANDA_ACCOUNT_ID is not set")
