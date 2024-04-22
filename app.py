import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# create tables   //used CS50 Duck for table IF NOT EXISTS and that was super helpful, also to make small adjustments to the CREATE TABLES
db.execute("CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, symbol TEXT NOT NULL, shares INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS stocks (user_id INTEGER, stock_name TEXT, quantity INTEGER)")
db.execute("CREATE TABLE IF NOT EXISTS transactions (user_id INTEGER, stock_name TEXT, quantity INTEGER, price NUMERIC, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")


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
    """Show portfolio of stocks"""
    # Query database for user's stocks and shares, USED THE CS50Duck to  build a skeleton of how this would look
    stocks = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id",
                        user_id=session["user_id"])

    # Query database for user's cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])

    # Initialize total value of stocks
    total_value = 0

    # For each stock, get current price and calculate total value
    for stock in stocks:
        current_price = lookup(stock["symbol"])
        stock["price"] = current_price['price']
        # Call lookup function to get current price
        stock_info = lookup(stock["symbol"])

        # Calculate total value of this stock (shares * price)
        total = stock['shares'] * stock_info['price']
        stock["total"] = total
        # Add this stock's total value to total_value
        total_value += total

    # Calculate grand total (stocks' total value + cash) outside the loop
    grand_total = total_value + cash[0]['cash']
    cash_balance = cash[0]['cash']
    # Pass all necessary data to the template  THE DUCK HELPED ALOT BECAUSE I DIDNT KNOW YOU CAN ADD MULTIPLE commas to the render templates
    return render_template("homepage.html", stocks=stocks, cash=cash, total_value=total_value, cash_balance=cash_balance, total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        try:
            shares = float(request.form.get("shares"))
            if not shares.is_integer() or shares <= 0:
                raise ValueError("Shares must be a positive whole number.")
            shares = int(shares)  # If we've made it here, it's safe to convert to int
        except ValueError as e:
            # Handle the error: show a message to the user, return a response with status 400, etc.  The duck helped alot with skeleton on each function
            return apology("Invalid Share amount", 400)

            # Check if the stock exists
        if stock is not None and shares > 0:
            # Calculate the total cost of the purchase
            price = stock['price'] * shares

            # Fetch the user's current balance
            rows = db.execute("SELECT cash FROM users WHERE id = :user_id",
                              user_id=session["user_id"])
            total = rows[0]["cash"]

            # Check if the user can afford the purchase
            if price <= total:
                total = total - price
                # Proceed with the transaction
                db.execute("UPDATE users SET cash = :new_total WHERE id = :user_id",
                           new_total=total, user_id=session["user_id"])

                rows = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id AND symbol = :symbol",
                                  user_id=session["user_id"], symbol=symbol)
                # If the user already owns shares of the stock | duck helped with new and old shares, didnt know i had to define each one
                old_shares = db.execute(
                    "SELECT shares FROM portfolio WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
                old_shares = old_shares[0]["shares"] if old_shares else 0
                new_shares = old_shares + shares
                if len(rows) > 0:
                    # Update the number of shares | duck helped a bit with the intricacies of the update and insert SQL
                    db.execute("UPDATE portfolio SET shares = :new_shares WHERE user_id = :user_id AND symbol = :symbol",
                               new_shares=new_shares, user_id=session["user_id"], symbol=symbol)
                else:
                    # Insert a new record
                    db.execute("INSERT INTO portfolio (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)",
                               user_id=session["user_id"], symbol=symbol, shares=shares)

                db.execute("INSERT INTO transactions (user_id, stock_name, quantity, price) VALUES (:user_id, :stock_name, :quantity, :price)",
                           user_id=session["user_id"], stock_name=symbol, quantity=shares, price=price)
                return redirect("/")
            else:
                # Return an apology message
                return apology("You can't afford this purchase.")
        else:
            # Return an apology message
            return apology("Invalid stock symbol.")
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = :user_id", user_id=session["user_id"])
    for transaction in transactions:
        if transaction['quantity'] > 0:
            transaction['type'] = ''
        elif transaction['quantity'] < 0:
            transaction['type'] = '-'
            transaction['quantity'] = -transaction['quantity']
        else:
            transaction['type'] = '0'
    return render_template("history.html", stocks=transactions)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        stocks = db.execute("SELECT * FROM stocks WHERE user_id = :user_id",
                            user_id=session["user_id"])
        return render_template("homepage.html", stocks=stocks)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Duck helped with the definitions of symbol and stock
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        if stock:
            return render_template("quoted.html", stock=stock)
        if not stock:
            flash("Invalid stock symbol", "danger")
            return apology("Invalid stock symbol", 400)
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        """ first 3 request.form.get was from LOGIN with slight alterations """

        """ cs50.ai said i have to go into my table (query) to check if theres a username already """
        username = request.form.get("username")
        user = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        if user:
            return apology("username already taken", 400)

        else:
            hashed_password = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                       username=username, hash=hashed_password)
            new_user_id = db.execute(
                "SELECT id FROM users WHERE username = :username", username=username)
            session["user_id"] = new_user_id[0]['id']
            return redirect("/")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    stocks = db.execute("SELECT symbol FROM portfolio WHERE user_id = ?", session["user_id"])
    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        shares = int(request.form.get("shares"))
        # I used many things from buy in the sell function. honestly this looks messy but it works fine, cs50 duck helped much with these functions
        if stock and shares > 0:
            rows = db.execute(
                "SELECT shares FROM portfolio WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
            if len(rows) == 0 or rows[0]["shares"] < shares:
                return apology("not enough shares", 400)
            db.execute("UPDATE portfolio SET shares = shares - ? WHERE user_id = ? AND symbol = ?",
                       shares, session["user_id"], symbol)
            price = stock['price'] * shares
            rows = db.execute("SELECT cash FROM users WHERE id = :user_id",
                              user_id=session["user_id"])
            total = rows[0]["cash"] + price
            db.execute("UPDATE users SET cash = :new_total WHERE id = :user_id",
                       new_total=total, user_id=session["user_id"])
            rows = db.execute(
                "SELECT shares FROM portfolio WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
            if rows[0]["shares"] == 0:
                db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol = ?",
                           session["user_id"], symbol)
            db.execute("INSERT INTO transactions (user_id, stock_name, quantity, price) VALUES (:user_id, :stock_name, :quantity, :price)",
                       user_id=session["user_id"], stock_name=symbol, quantity=shares, price=price)
            return redirect("/")

        elif shares > rows[0]["shares"]:
            return apology("you can't sell more shares than you own", 400)
        else:
            return apology("no or shares", 400)

    return render_template("sell.html", stocks=stocks)
