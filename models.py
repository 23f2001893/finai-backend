from database import db
from datetime import datetime

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,nullable=False,unique=True)
    email=db.Column(db.String,unique=True)
    password=db.Column(db.String) 
    phone=db.Column(db.String)
    pan=db.Column(db.String)
 
       