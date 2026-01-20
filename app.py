from flask import Flask,render_template,redirect,request,session
import mysql.connector

app = Flask(__name__)
app.secret_key = "bank_secret"

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "your_password in db",
    database = "bank_app"
)
cursor = db.cursor()

@app.route("/")
def home():
    return render_template("index.html")
5

@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].title()
        age = request.form["age"]
        dob = request.form["dob"]
        aadhar = request.form["aadhar"]
        phone = request.form["phone"]
        email = request.form["email"]
        place = request.form["place"]
        address = request.form["address"]
        password = request.form["password"]
        cursor.execute(
                "INSERT INTO users (name,age,dob,aadhar,phone,email,place,address,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (name,age,dob,aadhar,phone,email,place,address,password))
        db.commit()

        return redirect("/login")
    return render_template("register.html")





@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("select * from users where email =%s and password = %s",(email,password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect ("/user_home")

    return render_template ("login.html")    




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")






@app.route("/user_home")
def user_home():
    if "user_id" not in session:
        return redirect("/login")
    cursor.execute("select * from users where id = %s",(session["user_id"],))
    user = cursor.fetchone()

    cursor.execute("select type,amount,date from transactions where user_id = %s order by id DESC limit 5",(session["user_id"],))
    transactions = cursor.fetchall()

    return render_template("user_home.html",user=user,transactions=transactions)






@app.route("/profile",methods = ["GET","POST"])
def profile():
    if "user_id" not in session:
        return redirect ("/login")
    
    if request.method == "POST":
        name = request.form["name"].title()
        age = request.form["age"]
        phone = request.form["phone"]
        place = request.form["place"]
        address = request.form["address"]
    
        cursor.execute("Update  users set name =%s,age=%s, phone=%s, place=%s, address=%s where id =%s",(name, age, phone, place, address,session["user_id"]))
        db.commit()

    cursor.execute("select * from users where id = %s",(session["user_id"],))
    user = cursor.fetchone()
    return render_template("profile.html",user=user)



@app.route("/deposit",methods=["GET","POST"])
def deposit():
    if "user_id" not in session:
        return redirect ("/login")
    cursor.execute("select balance from users where id = %s",(session["user_id"],))
    balance = cursor.fetchone()[0]

    if request.method == "POST":
        amount = float(request.form["amount"])

        cursor.execute("update users set balance = balance + %s  where id = %s",(amount,session["user_id"]))
        cursor.execute("insert into transactions (user_id,type,amount)values(%s,%s,%s)",(session["user_id"],"Deposit",amount))
        db.commit()

        return redirect("/user_home")
    return render_template("deposit.html",balance=balance)




@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "user_id" not in session:
        return redirect("/login")
    error = None
    cursor.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
    balance = cursor.fetchone()[0]

    if request.method == "POST":
        amount = float(request.form["amount"])

        if  amount > balance:
            error = "Insufficient Balance"
        else:
            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s",
                (amount, session["user_id"]))
            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount) VALUES (%s, %s, %s)",
                (session["user_id"], "Withdraw", amount))
            db.commit()
            return redirect("/user_home")

    return render_template("withdraw.html",balance=balance,error=error)

    
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")
    
    cursor.execute("select * from transactions where user_id =%s",(session["user_id"],))
    records = cursor.fetchall()
    return render_template ("history.html",records=records)




if __name__ == "__main__":
    app.run(debug=True)


