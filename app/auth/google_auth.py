from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os

config_data = {
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
}
config = Config(environ=config_data)

oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config_data["GOOGLE_CLIENT_ID"],
    client_secret=config_data["GOOGLE_CLIENT_SECRET"],
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={
        'scope': 'openid email profile',  # PHẢI có openid
        'token_endpoint_auth_method': 'client_secret_post'
    },
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)
