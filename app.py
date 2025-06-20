from flask import Flask
from utils.routes import ADMIN_API_ROUTES, PUBLIC_ROUTES, PUBLIC_API_ROUTES
from utils.client import Client
import os

app = Flask(__name__)

client = Client("data.json")

app.config["SECRET_KEY"] = os.urandom(64).hex()
app.config["WORTHIT_USERNAME"] = os.environ.get("WORTHIT_USERNAME", "Luminoria")
app.config["WORTHIT_PASSWORD"] = os.environ.get(
    "WORTHIT_PASSWORD",
    "$argon2id$v=19$m=65540,t=3,p=4$SlU1NFJwL0VzTG9vbWVqL1BxWjhYMS9rc212eEh1VnZ0VFpPd0twanVEcz0$nCXmjHzbzfkSOpbYYekjmf/4IIKrpEhDgQO+0tEI+bQ",   # default: password
)

# 注册蓝图
app.register_blueprint(ADMIN_API_ROUTES, url_prefix="/api/admin")
app.register_blueprint(PUBLIC_ROUTES, url_prefix="/")
app.register_blueprint(PUBLIC_API_ROUTES, url_prefix="/api/public")

if __name__ == "__main__":
    app.client = client
    app.run(host="0.0.0.0", port=5000, debug=False)
