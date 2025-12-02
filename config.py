from urllib.parse import quote

class Config():
    DEBUG=False
    SQLALCHEMY_TRACK_MODIFICATION=False

class LocalDevelopmentConfig(Config):
    DEBUG=True
    password = quote("Lalit@1234", safe="")
    SQLALCHEMY_DATABASE_URI=f"postgresql://postgres:{password}@db.nedijqzlukcegqpqgbsg.supabase.co:5432/postgres"
    JWT_SECRET_KEY="this-is-a-secret-key"