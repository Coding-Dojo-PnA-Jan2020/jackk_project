from flask import Flask, session, redirect, render_template, request, flash
from mysqlconnect import connectToMySQL
from flask_bcrypt import Bcrypt
import re
import pylint

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'shrimpy'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$'
)

@app.route("/")
def landing_page():
    mysql = connectToMySQL('beam')
    return render_template("login.html")

@app.route("/regis", methods=['POST'])
def regis():
    #validation
    is_valid = True

    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("pleaes use a valid email address")

    if len(request.form['first_name'])< 1:
        is_valid = False
        flash("please enter more than 1 character")

    if len(request.form['last_name'])<2:
        is_valid = False
        flash('please enter more than 2 characters')

    if len(request.form['email'])<3:
        is_valid = False
        flash("please enter more than 3 characters")

    if request.form['password'] != request.form['c_password']:
        is_valid =  False
        flash("passwords must match")

    if not is_valid:
        return redirect("/")
    else:
        ## save to database
        mysql = connectToMySQL('beam')
        query = "INSERT into users(first_name, last_name, email, password, c_password, created_at, updated_at) VALUES(%(fn)s, %(ln)s, %(em)s, %(ps)s, %(cp)s, NOW(), NOW())"
        hashed_pw = bcrypt.generate_password_hash(request.form['password'])
        data = {
            'fn': request.form['first_name'],
            'ln': request.form['last_name'],
            'em': request.form['email'],
            'ps': request.form['password'],
            'cp': request.form['c_password'],
        }
        results = mysql.query_db(query, data) #[false, empytlist[], primary_key number ]
        if results:
            session['user_id'] = results
        return redirect("/success")

@app.route("/login", methods =['POST'])
def login():
    is_valid = True
    if len(request.form['email'])<1:
        is_valid = False
        flash("Not valid email")

    mysql = connectToMySQL('beam')  
    query = " SELECT * FROM users WHERE email = %(em)s"
    data = { "em": request.form['email']}
    result = mysql.query_db(query,data)

    if result:
        user_data = result[0]
        bcrypt.check_password_hash(user_data['password'], request.form['password'])
        session['user_id'] = user_data['user_id']
        return redirect("/success")
    else:
        is_valid = False
    if not is_valid:
        flash("email does not exist or invalid password")  
        return redirect("/")

@app.route("/success")
def home():
    mysql = connectToMySQL('beam')
    query = "SELECT first_name, last_name FROM users WHERE user_id = %(id)s"
    data = {
        'id': session['user_id']
    }
    result = mysql.query_db(query,data)
    if result:
        user_data = result[0]

    return render_template('index.html', user_data=user_data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if "__main__" == __name__:
    app.run(debug=True, port = 5002)