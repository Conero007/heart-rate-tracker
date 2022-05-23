from .user import get_user, save_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, render_template, redirect, request, flash, url_for

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user(email)
        print(user)

        if user and check_password_hash(user.password, password):
            flash("Logged in successfully!", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.home"))
        else:
            flash("Incorrect username or password.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    current_user.camera.release()
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = get_user(email)

        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(full_name) < 2:
            flash("First Name must be greater than 1 characters.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password2) <= 3:
            flash("Password must be greater than 3 characters.", category="error")
        else:
            save_user(
                email=email,
                full_name=full_name,
                password=generate_password_hash(password1)
            )

            login_user(get_user(email=email), remember=True)
            flash("Account created!", category="success")

            return redirect(url_for("views.home"))

    return render_template("signup.html", user=current_user)
