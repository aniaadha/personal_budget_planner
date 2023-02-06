import os
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
from datetime import datetime
import app
import io


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from helpers import apology, login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():


    return render_template("index.html")



@app.route("/budget_history", methods=["GET", "POST"])
@login_required
def budget_history():
    """See budgets"""
    rows = db.execute("SELECT budget_name, timestamp FROM budget WHERE user_id=:user_id", user_id=session["user_id"])
    budgets =[]
    for row in rows:
        budgets.append({
            "budget_name": row["budget_name"],
            "timestamp": row["timestamp"]
        })
    if not budgets:
        flash("It seems you have no budget history yet.")

    return render_template("budget_history.html", budgets=budgets)



@app.route("/report_budget", methods=["GET", "POST"])
@login_required
def report_budget():
    report_budget = request.form.get("budget")
    total_income = 0
    total_expenses = 0
    atotal_income = 0
    atotal_expenses = 0
    projected_balance = 0
    actual_balance = 0
    alert = 0
    max_exp = 0
    max_val = 0


    incomes = db.execute("SELECT salary, allowances, dividends, other FROM budget WHERE budget_name=:budget_name AND user_id=:user_id ORDER by id DESC LIMIT 1", budget_name=report_budget, user_id=session["user_id"])
    for income in incomes:
        total_income = (income["salary"] + income["allowances"] + income["dividends"] + income["other"])
    expenses = db.execute("SELECT groceries, health, clothing, fuel_car_maintenance, entertainment, home_supplies, electricity, gas, water, internet, telephone, otherexp FROM budget WHERE budget_name=:budget_name AND user_id=:user_id ORDER by id DESC LIMIT 1", budget_name=report_budget, user_id=session["user_id"])
    for expense in expenses:
        total_expenses = (expense["groceries"] + expense["health"] + expense["clothing"] + expense["fuel_car_maintenance"] + expense["entertainment"] + expense["home_supplies"]+ expense["electricity"] + expense["gas"] + expense["water"] + expense["internet"] + expense["telephone"] + expense["otherexp"])

    aincomes = db.execute("SELECT asalary, aallowances, adividends, aother FROM budget WHERE budget_name=:budget_name AND user_id=:user_id ORDER by id DESC LIMIT 1", budget_name=report_budget, user_id=session["user_id"])
    for aincome in aincomes:
        atotal_income = (aincome["asalary"] + aincome["aallowances"] + aincome["adividends"] + aincome["aother"])
    aexpenses = db.execute("SELECT agroceries, ahealth, aclothing, afuel_car_maintenance, aentertainment, ahome_supplies, aelectricity, agas, awater, ainternet, atelephone, aotherexp FROM budget WHERE budget_name=:budget_name AND user_id=:user_id ORDER by id DESC LIMIT 1", budget_name=report_budget, user_id=session["user_id"])
    for aexpense in aexpenses:
        atotal_expenses = (aexpense["agroceries"] + aexpense["ahealth"] + aexpense["aclothing"] + aexpense["afuel_car_maintenance"] + aexpense["aentertainment"] + aexpense["ahome_supplies"] + aexpense["aelectricity"] + aexpense["agas"] + aexpense["awater"] + aexpense["ainternet"] + aexpense["atelephone"] + aexpense["aotherexp"])

        projected_balance = total_income - total_expenses
        actual_balance = atotal_income - atotal_expenses
        if(actual_balance > 0):
            alert = "Well done! You spend less than you earn."
        elif(actual_balance < 0):
            alert = "It seems that you have overspent. Read Tips how to budget smartly."
        else:
             alert = "You spend the same as you earn. Think how to limit yor spending. Read Tips how to budget smartly."



        rows = db.execute("SELECT agroceries, ahealth, aclothing, afuel_car_maintenance, aentertainment, ahome_supplies, aelectricity, agas, awater, ainternet, atelephone, aotherexp FROM budget WHERE budget_name=:budget_name AND user_id=:user_id ORDER by id DESC LIMIT 1", budget_name=report_budget, user_id=session["user_id"])
        exp_val = []
        max_val = 0
        for row in rows:
            exp_val.append({
                row["agroceries"],
                row["ahealth"],
                row["aclothing"],
                row["afuel_car_maintenance"],
                row["aentertainment"],
                row["ahome_supplies"],
                row["aelectricity"],
                row["agas"],
                row["awater"],
                row["ainternet"],
                row["atelephone"],
                row["aotherexp"]
             })

        exp_val = [row["agroceries"], row["ahealth"], row["aclothing"], row["afuel_car_maintenance"], row["aentertainment"], row["ahome_supplies"], row["aelectricity"], row["agas"], row["awater"], row["ainternet"], row["atelephone"], row["aotherexp"] ]
        # find max value of expenses
        max_val = max(exp_val)
        # create list of expenses
        exp_cat = ['Groceries', 'Health', 'Clothing', 'Fuel & car maintenance', 'Entertainment', 'Home supplies', 'Electricity', 'Gas', 'Water', 'Internet', 'Telephone', 'Other expenses']

       # find index of max value
        max_exp_index = exp_val.index(max(exp_val))
        # find expense category
        a = np.array(exp_cat)
        ind_pos = np.array(max_exp_index)
        max_exp = a[ind_pos]



    return render_template("report_budget.html", report_budget=report_budget, total_income=total_income, total_expenses=total_expenses, atotal_income=atotal_income, atotal_expenses=atotal_expenses,
        projected_balance=projected_balance, actual_balance=actual_balance, alert=alert, max_exp=max_exp, max_val=max_val, incomes=incomes, aincomes=aincomes, expenses=expenses, aexpenses=aexpenses)

@app.route("/tips")
def tips():

    return render_template("tips.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username=:username", username=request.form.get("username"))
        if not request.form.get("username"):
            return apology("provide username")
        if len(rows) != 0:
            return apology("username is taken")
        if not request.form.get("password"):
            return apology("provide password")
        if not request.form.get("confirmation") == request.form.get("password"):
            return apology("provide the same password")

        a = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                       username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        session["user_id"] = a
        flash("Registered!")
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/getstarted", methods=["GET", "POST"])
@login_required
def getstarted():
    if request.method == "POST":
        budget_name = request.form.get("budget_name")
        salary = request.form.get("salary")
        allowances = request.form.get("allowances")
        dividends = request.form.get("dividends")
        other = request.form.get("other")
        asalary = request.form.get("asalary")
        aallowances = request.form.get("aallowances")
        adividends = request.form.get("adividends")
        aother = request.form.get("aother")
        groceries = request.form.get("groceries")
        health = request.form.get("health")
        clothing = request.form.get("clothing")
        fuel_car_maintenance = request.form.get("fuel_car_maintenance")
        entertainment = request.form.get("entertainment")
        home_supplies = request.form.get("home_supplies")
        electricity = request.form.get("electricity")
        gas = request.form.get("gas")
        water = request.form.get("water")
        internet = request.form.get("internet")
        telephone = request.form.get("telephone")
        agroceries = request.form.get("agroceries")
        ahealth = request.form.get("ahealth")
        aclothing = request.form.get("aclothing")
        afuel_car_maintenance = request.form.get("afuel_car_maintenance")
        aentertainment = request.form.get("aentertainment")
        ahome_supplies = request.form.get("ahome_supplies")
        aelectricity = request.form.get("aelectricity")
        agas = request.form.get("agas")
        awater = request.form.get("awater")
        ainternet = request.form.get("ainternet")
        atelephone = request.form.get("atelephone")
        aotherexp = request.form.get("aotherexp")
        otherexp = request.form.get("otherexp")
        if not budget_name:
            return apology("Provide your budget name!")
        if not salary or not allowances or not dividends or not other or not asalary or not aallowances or not adividends or not aother or not groceries or not health or not clothing or not fuel_car_maintenance or not entertainment or not home_supplies or not electricity or not gas or not water or not internet or not telephone or not otherexp or not agroceries or not ahealth or not aclothing or not afuel_car_maintenance or not aentertainment or not ahome_supplies or not aelectricity or not agas or not awater or not ainternet or not atelephone or not aotherexp:
            return apology("Invalid amount")
        else:
            db.execute("INSERT INTO budget (user_id, budget_name, timestamp, salary, allowances, dividends, other, asalary, aallowances, adividends, aother, groceries, health, clothing, fuel_car_maintenance, entertainment, home_supplies, electricity, gas, water, internet, telephone, otherexp, agroceries, ahealth, aclothing, afuel_car_maintenance, aentertainment, ahome_supplies, aelectricity, agas, awater, ainternet, atelephone, aotherexp) VALUES (:user_id, :budget_name, :timestamp, :salary, :allowances, :dividends, :other, :asalary, :aallowances, :adividends, :aother, :groceries, :health, :clothing, :fuel_car_maintenance, :entertainment, :home_supplies, :electricity, :gas, :water, :internet, :telephone, :otherexp, :agroceries, :ahealth, :aclothing, :afuel_car_maintenance, :aentertainment, :ahome_supplies, :aelectricity, :agas, :awater, :ainternet, :atelephone, :aotherexp)",
                    user_id = session["user_id"],
                    budget_name = request.form.get("budget_name"),
                    timestamp = datetime.now(),
                    salary = request.form.get("salary"),
                    allowances = request.form.get("allowances"),
                    dividends = request.form.get("dividends"),
                    other = request.form.get("other"),
                    asalary = request.form.get("asalary"),
                    aallowances = request.form.get("aallowances"),
                    adividends = request.form.get("adividends"),
                    aother = request.form.get("aother"),
                    groceries = request.form.get("groceries"),
                    health = request.form.get("health"),
                    clothing = request.form.get("clothing"),
                    fuel_car_maintenance = request.form.get("fuel_car_maintenance"),
                    entertainment = request.form.get("entertainment"),
                    home_supplies = request.form.get("home_supplies"),
                    electricity = request.form.get("electricity"),
                    gas = request.form.get("gas"),
                    water = request.form.get("water"),
                    internet = request.form.get("internet"),
                    telephone = request.form.get("telephone"),
                    otherexp = request.form.get("otherexp"),
                    agroceries = request.form.get("agroceries"),
                    ahealth = request.form.get("ahealth"),
                    aclothing = request.form.get("aclothing"),
                    afuel_car_maintenance = request.form.get("afuel_car_maintenance"),
                    aentertainment = request.form.get("aentertainment"),
                    ahome_supplies = request.form.get("ahome_supplies"),
                    aelectricity = request.form.get("aelectricity"),
                    agas = request.form.get("agas"),
                    awater = request.form.get("awater"),
                    ainternet = request.form.get("ainternet"),
                    atelephone = request.form.get("atelephone"),
                    aotherexp = request.form.get("aotherexp")
                     )

        flash("Done! Now see your summary.")
        return redirect("/summary")
    else:
        return render_template("getstarted.html")

@app.route("/summary", methods=["GET", "POST"])
@login_required

def summary():

    total_income = 0
    total_expenses = 0
    atotal_income = 0
    atotal_expenses = 0
    projected_balance = 0
    actual_balance = 0
    alert = 0
    max_exp = 0
    max_val = 0

    "See the summary"
    rows = db.execute("SELECT budget_name FROM budget WHERE user_id=:user_id ORDER by id DESC LIMIT 1", user_id=session["user_id"])
    budget_name =[]
    for row in rows:
        budget_name.append({
            row["budget_name"],
            })
    budget_name = row["budget_name"]
    incomes = db.execute("SELECT salary, allowances, dividends, other FROM budget WHERE user_id=:user_id ORDER by id DESC LIMIT 1", user_id=session["user_id"])
    for income in incomes:
        total_income = (income["salary"] + income["allowances"] + income["dividends"] + income["other"])
    expenses = db.execute("SELECT groceries, health, clothing, fuel_car_maintenance, entertainment, home_supplies, electricity, gas, water, internet, telephone, otherexp FROM budget WHERE user_id=:user_id ORDER by id DESC LIMIT 1", user_id=session["user_id"])
    for expense in expenses:
        total_expenses = (expense["groceries"] + expense["health"] + expense["clothing"] + expense["fuel_car_maintenance"] + expense["entertainment"] + expense["home_supplies"]+ expense["electricity"] + expense["gas"] + expense["water"] + expense["internet"] + expense["telephone"] + expense["otherexp"])

    aincomes = db.execute("SELECT asalary, aallowances, adividends, aother FROM budget WHERE user_id=:user_id ORDER by id DESC LIMIT 1", user_id=session["user_id"])
    for aincome in aincomes:
        atotal_income = (aincome["asalary"] + aincome["aallowances"] + aincome["adividends"] + aincome["aother"])
    aexpenses = db.execute("SELECT agroceries, ahealth, aclothing, afuel_car_maintenance, aentertainment, ahome_supplies, aelectricity, agas, awater, ainternet, atelephone, aotherexp FROM budget WHERE user_id=:user_id ORDER by id DESC LIMIT 1", user_id=session["user_id"])
    for aexpense in aexpenses:
        atotal_expenses = (aexpense["agroceries"] + aexpense["ahealth"] + aexpense["aclothing"] + aexpense["afuel_car_maintenance"] + aexpense["aentertainment"] + aexpense["ahome_supplies"] + aexpense["aelectricity"] + aexpense["agas"] + aexpense["awater"] + aexpense["ainternet"] + aexpense["atelephone"] + aexpense["aotherexp"])

        projected_balance = total_income - total_expenses
        actual_balance = atotal_income - atotal_expenses
        if(actual_balance > 0):
            alert = "Well done! You spend less than you earn."
        elif(actual_balance < 0):
            alert = "It seems that you have overspent. Read Tips how to budget smartly."
        else:
             alert = "You spend the same as you earn. Think how to limit yor spending. Read Tips how to budget smartly."



        rows = db.execute("SELECT agroceries, ahealth, aclothing, afuel_car_maintenance, aentertainment, ahome_supplies, aelectricity, agas, awater, ainternet, atelephone, aotherexp FROM budget WHERE user_id=:user_id ORDER by id DESC LIMIT 1", user_id=session["user_id"])
        exp_val = []
        max_val = 0
        for row in rows:
            exp_val.append({
                row["agroceries"],
                row["ahealth"],
                row["aclothing"],
                row["afuel_car_maintenance"],
                row["aentertainment"],
                row["ahome_supplies"],
                row["aelectricity"],
                row["agas"],
                row["awater"],
                row["ainternet"],
                row["atelephone"],
                row["aotherexp"]
             })

        exp_val = [row["agroceries"], row["ahealth"], row["aclothing"], row["afuel_car_maintenance"], row["aentertainment"], row["ahome_supplies"], row["aelectricity"], row["agas"], row["awater"], row["ainternet"], row["atelephone"], row["aotherexp"] ]
        # find max value of expenses
        max_val = max(exp_val)
        # create list of expenses
        exp_cat = ['groceries', 'health', 'clothing', 'fuel_car_maintenance', 'entertainment', 'home_supplies', 'electricity', 'gas', 'water', 'internet', 'telephone', 'otherexp']

       # find index of max value
        max_exp_index = exp_val.index(max(exp_val))
        # find expense category
        a = np.array(exp_cat)
        ind_pos = np.array(max_exp_index)
        max_exp = a[ind_pos]





    return render_template("summary.html", total_income=total_income, total_expenses=total_expenses, atotal_income=atotal_income, atotal_expenses=atotal_expenses,
        projected_balance=projected_balance, actual_balance=actual_balance, alert=alert, max_exp=max_exp, max_val=max_val, budget_name=budget_name)




@app.route('/pie_plot.png')
def pie_plot_png():
    figure = create_figure()
    output = io.BytesIO()
    FigureCanvas(figure).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    figure, ax1 = plt.subplots(figsize = (8,4))

    figure.patch.set_facecolor('#E8E5DA')

    rows = db.execute("SELECT agroceries, ahealth, aclothing, afuel_car_maintenance, aentertainment, ahome_supplies, aelectricity, agas, awater, ainternet, atelephone, aotherexp FROM budget WHERE user_id=:user_id ORDER BY id DESC LIMIT 1", user_id=session["user_id"])
    exp_val = []
    for row in rows:
        exp_val.append({
            row["agroceries"],
            row["ahealth"],
            row["aclothing"],
            row["afuel_car_maintenance"],
            row["aentertainment"],
            row["ahome_supplies"],
            row["aelectricity"],
            row["agas"],
            row["awater"],
            row["ainternet"],
            row["atelephone"],
            row["aotherexp"]
            })

    budgets = [row["agroceries"], row["ahealth"], row["aclothing"], row["afuel_car_maintenance"], row["aentertainment"], row["ahome_supplies"], row["aelectricity"], row["agas"], row["awater"], row["ainternet"], row["atelephone"], row["aotherexp"] ]
    labels = ['Groceries', 'Health', 'Clothing', 'Fuel & car maintenance', 'Entertainment', 'Home supplies', 'Electricity', 'Gas', 'Water', 'Internet', 'Telephone', 'Other expenses']
    ax1.pie(budgets, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax1.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.

    return figure

if __name__ == '__main__':
    app.run(debug = True)





