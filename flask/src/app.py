import os
import sys

from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor


FLASK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FLASK_DIR)

from src.api.prelude import init_api
from src.api.v1.auth import auth_routes
from src.api.v1.devices import device_routes
from src.api.v1.oauth import oauth_routes
from src.api.v1.permissions import permission_routes
from src.api.v1.roles import role_routes
from src.api.v1.users import user_routes
from src.cli.users import user_commands
from src.db.cache import init_cache
from src.tools.tracer import configure_tracer


configure_tracer()

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


# ROUTES
app.register_blueprint(auth_routes)
app.register_blueprint(oauth_routes)
app.register_blueprint(user_routes)
app.register_blueprint(role_routes)
app.register_blueprint(permission_routes)
app.register_blueprint(device_routes)

# CLI
app.register_blueprint(user_commands)


init_api(app)
init_cache()
