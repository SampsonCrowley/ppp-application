# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
# from flask_login import login_required, login_user, logout_user

# from ppp_application.extensions import login_manager
# from ppp_application.public.forms import LoginForm
# from ppp_application.user.forms import RegisterForm
# from ppp_application.user.models import User
from ppp_application.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")

@blueprint.route("/", methods=["GET", "POST"])
def home():
    return redirect("/applications")

# @blueprint.route("/logout/")
# @login_required
# def logout():
#     """Logout."""
#     logout_user()
#     flash("You are logged out.", "info")
#     return redirect(url_for("public.home"))


# @blueprint.route("/register/", methods=["GET", "POST"])
# def register():
#     """Register new user."""
#     form = RegisterForm(request.form)
#     if form.validate_on_submit():
#         User.create(
#             username=form.username.data,
#             email=form.email.data,
#             password=form.password.data,
#             active=True,
#         )
#         flash("Thank you for registering. You can now log in.", "success")
#         return redirect(url_for("public.home"))
#     else:
#         flash_errors(form)
#     return render_template("public/register.html", form=form)


# @blueprint.route("/about/")
# def about():
#     """About page."""
#     form = LoginForm(request.form)
#     return render_template("public/about.html", form=form)
