#!/usr/bin/env python3

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from web import auth


auth_routes = Blueprint(
    "auth",
    __name__
)


@auth_routes.route("/login", methods=["GET", "POST"])
def login():

    if not auth.has_users():

        return redirect(
            url_for("auth.uninitialized")
        )

    if auth.current_user() is not None:

        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = auth.authenticate(
            username,
            password
        )

        if user is None:

            flash(
                "Invalid username or password.",
                "error"
            )

        else:

            auth.login_user(user)

            next_url = request.args.get(
                "next",
                ""
            )

            if (
                not next_url
                or not next_url.startswith("/")
                or next_url.startswith("//")
            ):

                next_url = url_for(
                    "dashboard.index"
                )

            return redirect(
                next_url
            )

    return render_template(
        "login.html"
    )


@auth_routes.route("/logout")
def logout():

    auth.logout_user()

    return redirect(
        url_for("auth.login")
    )


@auth_routes.route("/auth-uninitialized")
def uninitialized():

    return render_template(
        "uninitialized.html"
    )
