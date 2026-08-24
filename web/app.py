#!/usr/bin/env python3

import os
import sys

from flask import Flask


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

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    from web.routes.dashboard import (
        dashboard,
        network_is_healthy
    )

    from web.routes.api import api

    app.register_blueprint(
        dashboard
    )

    app.register_blueprint(
        api
    )

    app.jinja_env.globals[
        "network_is_healthy"
    ] = network_is_healthy

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )