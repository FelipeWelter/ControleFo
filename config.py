import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "7G[a5ov7GJcHVYj1")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_EVIDENCIAS_DIR = os.environ.get(
        "UPLOAD_EVIDENCIAS_DIR",
        os.path.join(BASE_DIR, "uploads", "evidencias")
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024