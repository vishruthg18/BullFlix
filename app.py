import binascii
from flask import Flask, render_template, redirect, request, url_for, flash
from db import connection
from forms import LoginForm, RegisterForm
from flask import session
from ratings import ratings_blueprint
import bcrypt


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.register_blueprint(ratings_blueprint)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

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
        cursor.execute("SELECT * FROM USERS")
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
            sql_query = "SELECT * FROM BULLFLIX.users WHERE EMAIL = :email"
            cursor.execute(sql_query, {"email":email})
            user = cursor.fetchone()
            if user:
                if password == str(user[3]):
                    session['username'] = user[1]
                    session['user_id'] = binascii.hexlify(user[0]).decode('utf-8')
                    print("session user id", session['user_id'])
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
            sql_query = "INSERT INTO BULLFLIX.USERS (EMAIL, USER_NAME, PIP_HASH) VALUES (:email, :username, :password)"
            cursor.execute(sql_query, {"email":email, "username":username, "password":password})
            connection.commit()
            cursor.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('login')



if __name__ == '__main__':
    app.run(debug=True)
