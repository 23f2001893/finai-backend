from sqlalchemy import Numeric
from database import db
from datetime import datetime
from datetime import date

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,nullable=False,unique=True)
    email=db.Column(db.String,unique=True)
    password=db.Column(db.String) 
    phone=db.Column(db.String)
    pan=db.Column(db.String)
class Income(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    month=db.Column(db.String,nullable=False)
    year=db.Column(db.String,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    amount=db.Column(Numeric(12,2),nullable=False)  
    user=db.relationship('User',backref=db.backref('incomes',lazy=True))    
class DailyExpense(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    date=db.Column(db.Date,default=date.today)
    category=db.Column(db.String,nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    user=db.relationship('User',backref=db.backref('daily_expenses',lazy=True))
class MonthlyExpense(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    month=db.Column(db.String,nullable=False)
    year=db.Column(db.String,nullable=False)
    rent=db.Column(db.Float,default=0.0)
    emi=db.Column(db.Float,default=0.0)
    subscriptions=db.Column(db.Float,default=0.0)
    others=db.Column(db.Float,default=0.0)
    user=db.relationship('User',backref=db.backref('monthly_expenses',lazy=True))
class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    amount = db.Column(Numeric(12, 2), default=0)
    start_date = db.Column(db.Date, default=date.today)
    tenure_months = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    kind = db.Column(db.String(20), nullable=False)  # "monthly", "fixed"
    investment_type = db.Column(db.String(50), nullable=False)  # "SIP", "FD", etc.
    roi = db.Column(db.Float, default=0.0)

    user = db.relationship('User', backref=db.backref('investments', lazy=True))
