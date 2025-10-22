from flask import Flask
from config import LocalDevelopmentConfig
from database import db
from models import *
from security import jwt
from flask_cors import CORS

from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini with key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app=None
def create_app():
    app=Flask(__name__)
    app.secret_key = "my_super_secret_key_12345"
    CORS(app,supports_credentials=True,origins=["http://localhost:5173","https://finai.vercel.app"])
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
  
    app.app_context().push()
    return app
app=create_app()



from routes import *
if __name__ == "__main__":

    app.run(debug=True)
