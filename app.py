from flask import Flask, render_template, redirect, request, url_for, flash
from forms import LoginForm, RegisterForm
from flask import session
import oracledb
import bcrypt

app = Flask(__name__)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Establish a connection to Oracle database
connection = oracledb.connect(
    user="BULLFLIX_WEB",
    password="usf1956!",
    dsn="reade.forest.usf.edu:1521/cdb9"
)
print("Successfully connected to Oracle Database")

# use sqlite for development
# import sqlite3
# connection = sqlite3.connect('bullflix.db', check_same_thread=False)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/users')
def display_users():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM BULLFLIX.USERS")
        users = cursor.fetchall()
        cursor.close()
        return render_template('users.html', users=users)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            cursor = connection.cursor()
            sql_query = "SELECT USER_GUID,EMAIL,USER_NAME,PIP_HASH FROM BULLFLIX.USERS_VW WHERE EMAIL = :email"
            cursor.execute(sql_query, {"email":email})
            user = cursor.fetchone()
            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user[3]):
                    session['username'] = user[1]
                    return redirect(url_for('index'))
                else:
                    flash('Login unsuccessful. Please check your email and password.', 'danger')
            else:
                flash('No user found with that email address.', 'danger')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
        
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        try:
            cursor = connection.cursor()

            # check if email or username already exists
            sql_query = "SELECT * FROM BULLFLIX.USERS WHERE EMAIL = :email or USER_NAME = :username"
            cursor.execute(sql_query, {"email":email, "username":username})
            user = cursor.fetchone()
            if user:
                flash('Email or username already exists. Please try again.', 'danger')
                return redirect(url_for('register'))

            # hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            print("hashed password ", hashed_password)

            # insert new user
            sql_query = "INSERT INTO BULLFLIX.USERS (EMAIL, USER_NAME, PIP_HASH) VALUES (:email, :username, ORA_HASH(:password))"
            cursor.execute(sql_query, {"email":email, "username":username, "password":password})
            connection.commit()
            cursor.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    return render_template('register.html', form=form)

@app.route('/getRatings', methods=['GET'])
def get_user_ratings():

        try:
            cursor = connection.cursor()
            sql_query = "SELECT movie_title,release_year,rating,rating_date FROM bullflix.ratings_vw WHERE user_hex_guid = :user_hex"
            cursor.execute(sql_query, {"user_hex":user_hex})
            movie_ratings = cursor.fetchall()
            cursor.close()
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')       
        return render_template('login.html', movie_ratings=movie_ratings)



@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('login')

if __name__ == '__main__':
    app.run(debug=True)
