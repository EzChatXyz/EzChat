from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin
from oauthlib.oauth2 import WebApplicationClient
import pymongo, datetime, humanize, requests, config, os, json, flask_socketio

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = config.google.id
GOOGLE_CLIENT_SECRET = config.google.secret
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

client = WebApplicationClient(GOOGLE_CLIENT_ID)

app = Flask("")
app.secret_key = config.secret_key

async_mode = None
socketio = flask_socketio.SocketIO(app, async_mode=async_mode, logger=True, engineio_logger=True)

class User(UserMixin):
  pass

users = {}
last_messages = []

login_manager = LoginManager()
login_manager.init_app(app)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@login_manager.user_loader
def user_loader(id):
    try:
        u = users[id]
    except KeyError:
        return None
    user = User()
    user.id=id
    user.name=u["name"]
    user.pic=u["pic"]
    return user

@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(token_endpoint,authorization_response=request.url,redirect_url=request.base_url,code=code)
    token_response = requests.post(token_url,headers=headers,data=body,auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),)
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        print("----------\n" + str(userinfo_response.json()) + "\n------------------")
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User()
    user.id=unique_id
    user.name=users_name
    user.email=users_email
    user.profile_pic=picture

    users[user.id] = {"name": user.name, "email": user.email, "pic": user.profile_pic}

    login_user(user)
    return redirect("/")

@socketio.on('connected')
def connected(data):
    socketio.emit("message", {"text": None, "user": None})
    print("connected")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if not current_user.is_authenticated:
            return render_template("not-logged.html", domain=config.domain, messages=last_messages)

        return render_template("index.html", user=current_user, domain=config.domain, messages=last_messages)

@socketio.on("new_message")
def new_message(data):
    if data["text"]:
        if len(last_messages) >= 5:
            last_messages.pop(0)
        last_messages.append(data)
    socketio.emit("message", data)

@app.route("/cdn/<file>")
def files(file):
    return send_file("cdn/" + file)

@app.route("/cdn/<folder>/<file>")
def folder_file(folder, file):
    return send_file("cdn/" + folder + "/" + file)

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#app.run(host="0.0.0.0",port=8080, debug=True)
socketio.run(app, host="0.0.0.0", port=config.port)
