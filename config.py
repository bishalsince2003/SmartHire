import os
from dotenv import load_dotenv

load_dotenv()

# Supports both local .env vars (DB_HOST, DB_USER, ...) and Railway's
# auto-injected MySQL plugin vars (MYSQLHOST, MYSQLUSER, ...) as a fallback.
DB_HOST = os.getenv("DB_HOST") or os.getenv("MYSQLHOST", "localhost")
DB_USER = os.getenv("DB_USER") or os.getenv("MYSQLUSER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD", "")
DB_NAME = os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE", "smarthire_db")
DB_PORT = os.getenv("DB_PORT") or os.getenv("MYSQLPORT", "3306")

SECRET_KEY = os.getenv("SECRET_KEY", "smarthire_secret_key")
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
