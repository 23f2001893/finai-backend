class Config():
    DEBUG=False
    SQLALCHEMY_TRACK_MODIFICATION=False
class LocalDevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI="postgresql://finai_db_yj7o_user:OQYIxeHizzd7upmgWfl3pAeuk1BVB67p@dpg-d3scecodl3ps73da09cg-a.oregon-postgres.render.com/finai_db_yj7o"
    JWT_SECRET_KEY="this-is-a-secret-key"
