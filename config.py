class Config():
    DEBUG=False
    SQLALCHEMY_TRACK_MODIFICATION=False
class LocalDevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI="postgresql://postgres:Lalit@1234@db.nedijqzlukcegqpqgbsg.supabase.co:5432/postgres"
    JWT_SECRET_KEY="this-is-a-secret-key"
