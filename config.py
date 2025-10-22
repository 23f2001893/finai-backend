class Config():
    DEBUG=False
    SQLALCHEMY_TRACK_MODIFICATION=False
class LocalDevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI="sqlite:///secureDb.sqlite3"
    JWT_SECRET_KEY="this-is-a-secret-key"
