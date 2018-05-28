from finance import api
from finance.auth.models import User


def register_api(app):
    api.create_api(User, app=app, methods=["GET"], primary_key='username')
