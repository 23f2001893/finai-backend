from flask import current_app as app,jsonify,request,session
from models import *
from decimal import Decimal
from sqlalchemy import func
from flask_jwt_extended import create_access_token,current_user,jwt_required,get_jwt_identity
from functools import wraps
import google.generativeai as genai
import os
import pandas as pd


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.route("/api/login",methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"message": "Wrong username or password"}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify({"access_token": access_token, "username": user.username}),200

from flask import request, jsonify

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid JSON"}), 400

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        phone = data.get("phone")
        pan = data.get("pan")

        if not all([username, password, email, phone, pan]):
            return jsonify({"message": "All fields are required"}), 400

        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({"message": "User already exists"}), 409

        # Add user
        new_user = User(username=username, password=password, email=email, phone=phone, pan=pan)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User added successfully"}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Internal server error"}), 500


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

@app.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    username = get_jwt_identity()  # retrieves the username from token
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "pan": user.pan
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    prompt = f"You are a friendly personal finance assistant helping users manage money and budgeting.\nUser: {user_message}"
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/custdata', methods=['POST'])
def custdata():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid JSON"}), 400

        food = data.get("ManualExpenseFood")
        clothing = data.get("ManualExpenseClothing")
        travel= data.get("manualExpenseTravel")
        education= data.get("ManualExpenseEducation")

        return jsonify({"message": "User added successfully"}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Internal server error"}), 500

@app.route("/analyze-expenses", methods=["POST"])
def analyze_expenses():
    try:
        # Check if file is uploaded
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Read the file
        if file.filename.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Convert to text summary (keep it short for the model)
        text_data = df.head(30).to_string(index=False)

        # Send to Gemini for categorization
        prompt = f"""
        You are a financial data analyst. 
        Categorize each transaction below into one of: Food, Clothing, Travel, Education
        Return the total spend in each category as JSON.
        Transactions:\n{text_data}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Extract clean JSON (Gemini usually returns code block)
        import re, json
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            data = {"error": "Could not parse AI response", "raw": response.text}

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/add-daily-expense", methods=["POST"])
def add_expense():
    data=request.get_json()
    date=data.get("date")
    category=data.get("category")
    amount=data.get("amount")
    username=data.get("username")
    user=User.query.filter_by(username=username).first()
    user_id=user.id
    new_expense=DailyExpense(user_id=user_id,date=date,category=category,amount=amount)
    db.session.add(new_expense)
    db.session.commit()
    new_id=new_expense.id
    return jsonify({
        "id":new_id,
        "date":date,
        "category":category,    
        "amount":amount
        
    }),200
@app.route("/api/delete-daily-expense/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = DailyExpense.query.get(expense_id)
    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted successfully"}), 200

@app.route("/api/get-daily-expenses", methods=["GET"])
def get_daily_expenses():
    username=request.args.get("username")
    date=request.args.get("date")   
    user=User.query.filter_by(username=username).first()
    if not user or not date:
        return jsonify({"message": "User or date not found"}), 404
    user_id=user.id
    expenses=DailyExpense.query.filter_by(user_id=user_id,date=date).all()
    expenses_list=[]
    for expense in expenses:
        expenses_list.append({
            "id":expense.id,
            "date":expense.date.strftime("%Y-%m-%d"),
            "category":expense.category,
            "amount":float(expense.amount)
        })
    return jsonify(expenses_list),200
@app.route("/api/add-monthly-expense", methods=["POST"])
def add_monthly_expense():
    data=request.get_json()
    month=data.get("month")
    year=data.get("year")
    rent=data.get("rent",0.0)
    emi=data.get("emi",0.0)
    subscriptions=data.get("subscriptions",0.0)
    others=data.get("others",0.0)
    username=data.get("username")
    user=User.query.filter_by(username=username).first()
    user_id=user.id
    new_expense=MonthlyExpense(user_id=user_id,month=month,year=year,rent=rent,emi=emi,subscriptions=subscriptions,others=others)
    db.session.add(new_expense)
    db.session.commit()
    new_id=new_expense.id
    return jsonify({
        "id":new_id,
        "month":month,
        "year":year,    
        "rent":rent,
        "emi":emi,
        "subscriptions":subscriptions,
        "others":others
        
    }),200
@app.route("/api/get-monthly-expenses/<string:username>", methods=["GET"])
def get_monthly_expenses(username):
    user=User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user_id=user.id
    expenses=MonthlyExpense.query.filter_by(user_id=user_id).all()
    expenses_list=[]
    for expense in expenses:
        expenses_list.append({
            "id":expense.id,
            "month":expense.month,
            "year":expense.year,
            "rent":expense.rent,
            "emi":expense.emi,
            "subscriptions":expense.subscriptions,
            "others":expense.others
        })
    return jsonify(expenses_list),200
@app.route("/api/add-investment", methods=["POST"])
def add_investment():
    data=request.get_json()
    amount=data.get("amount")
    start_date=data.get("start_date")
    tenure_months=data.get("tenure_months")
     # Calculate end_date based on tenure_months
    month = int(start_date.split("-")[1]) + tenure_months
    year = int(start_date.split("-")[0]) + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = int(start_date.split("-")[2])
    end_date = f"{year:04d}-{month:02d}-{day:02d}" 
    kind=data.get("kind")
    investment_type=data.get("investment_type")
    roi=data.get("roi",0.0)
    username=data.get("username")
    user=User.query.filter_by(username=username).first()
    user_id=user.id
    new_investment=Investment(user_id=user_id,amount=amount,start_date=start_date,tenure_months=tenure_months,end_date=end_date,kind=kind,investment_type=investment_type,roi=roi)
    db.session.add(new_investment)
    db.session.commit()
    new_id=new_investment.id
    return jsonify({
        "id":new_id,
        "amount":amount,
        "start_date":start_date,    
        "tenure_months":tenure_months,
        "end_date":end_date,
        "kind":kind,
        "investment_type":investment_type,
        "roi":roi
        
    }),200

@app.route("/api/monthly-summary", methods=["GET"])
def monthly_summary():
    username = request.args.get("username")
    month_index = request.args.get("month")  # "0".."11"
    year = request.args.get("year")          # string, e.g. "2025"

    if not username or month_index is None or year is None:
        return jsonify({"error": "username, month, and year are required"}), 400

    # validate & convert
    try:
        month_index_int = int(month_index)   # 0..11
        year_int = int(year)
    except ValueError:
        return jsonify({"error": "month and year must be integers"}), 400

    if not (0 <= month_index_int <= 11):
        return jsonify({"error": "month must be between 0 and 11"}), 400

    # Postgres extract('month', date) is 1..12 → convert 0-based to 1-based
    month_for_daily = month_index_int + 1    # 1..12

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 1️⃣ MonthlyExpense: income + fixed expenses for that month_index/year
    monthly = MonthlyExpense.query.filter_by(
        user_id=user.id,
        year=year,                 # stored as string
        month=str(month_index_int) # stored as "0".."11"
    ).first()

    def to_float(x):
        if x is None:
            return 0.0
        if isinstance(x, Decimal):
            return float(x)
        return float(x)

    income = to_float(monthly.income) if monthly else 0.0
    rent = to_float(monthly.rent) if monthly else 0.0
    emi = to_float(monthly.emi) if monthly else 0.0
    subscriptions = to_float(monthly.subscriptions) if monthly else 0.0
    others_fixed = to_float(monthly.others) if monthly else 0.0

    fixed_breakdown = {
        "Rent": rent,
        "EMI": emi,
        "Subscriptions": subscriptions,
        "Others (fixed)": others_fixed,
    }
    fixed_total = sum(fixed_breakdown.values())

    # 2️⃣ DailyExpense: variable expenses grouped by category for that calendar month
    variable_rows = (
        db.session.query(
            DailyExpense.category,
            func.sum(DailyExpense.amount).label("total_amount")
        )
        .filter(
            DailyExpense.user_id == user.id,
            func.extract("year", DailyExpense.date) == year_int,
            func.extract("month", DailyExpense.date) == month_for_daily,
        )
        .group_by(DailyExpense.category)
        .all()
    )

    variable_breakdown = {
        category: to_float(total_amount)
        for category, total_amount in variable_rows
    }
    variable_total = sum(variable_breakdown.values())

    # 3️⃣ Combine fixed + variable
    breakdown = {**fixed_breakdown, **variable_breakdown}
    total_expenses = fixed_total + variable_total
    savings = income - total_expenses

    return jsonify({
        "username": username,
        "year": year,
        "month_index": month_index_int,          # 0..11
        "month_for_daily": month_for_daily,      # 1..12 (for debugging)
        "income": income,
        "fixed_expenses_total": fixed_total,
        "variable_expenses_total": variable_total,
        "total_expenses": total_expenses,
        "savings": savings,
        "breakdown": breakdown,
    }), 200            
    
    
        
 