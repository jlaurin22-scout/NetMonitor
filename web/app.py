#!/usr/bin/env python3

import os
import sys

from flask import (
    Flask,
    redirect,
    request,
    url_for,
)


PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


if PROJECT_DIR not in sys.path:

    sys.path.insert(
        0,
        PROJECT_DIR
    )


def create_app():

    from web import auth

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.secret_key = auth.initialize()

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=28800,
    )

    from web.routes.dashboard import (
        dashboard,
        network_is_healthy
    )

    from web.routes.api import api
    from web.routes.auth import auth_routes
    from web.routes.configuration import configuration
    from web.routes.incidents import incidents
    from web.routes.events import events

    app.register_blueprint(
        dashboard
    )

    app.register_blueprint(
        api
    )

    app.register_blueprint(
        auth_routes
    )

    app.register_blueprint(
        configuration
    )

    app.register_blueprint(
        incidents
    )

    app.register_blueprint(
        events
    )

    app.jinja_env.globals[
        "network_is_healthy"
    ] = network_is_healthy

    app.context_processor(
        lambda: {
            "current_user": auth.current_user()
        }
    )

    @app.before_request
    def require_authentication():

        if request.endpoint in (
            "auth.login",
            "auth.logout",
            "auth.uninitialized",
            "static",
        ):

            return None

        if not auth.has_users():

            return redirect(
                url_for("auth.uninitialized")
            )

        if auth.current_user() is None:

            next_url = request.full_path

            if next_url.endswith("?"):

                next_url = next_url[:-1]

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        return None

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )