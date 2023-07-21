from fastapi import FastAPI, BackgroundTasks
from .schemas import UserBASE, UserInsert, Login, Token
from .controller import edit_user, delete_user, get_current_user, insert_user, authenticate_user, check_handle_availability
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

app = FastAPI()

conf = ConnectionConfig(
    MAIL_USERNAME = "ishanmitra010@outlook.com",
    MAIL_PASSWORD = "eczprwpgvigaibvs",
    MAIL_FROM = "ishanmitra010@outlook.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.office365.com",
    MAIL_FROM_NAME="Ishan Mitra",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

fm = FastMail(conf)

@app.get("/")
def index():
    return {"status":"ok"}

@app.get("/check")
def check(handle: str):
    return check_handle_availability(handle)

@app.post("/create")
def create(user: UserInsert, background_tasks: BackgroundTasks):
    r = insert_user(user)
    if r["success"]:
        message = MessageSchema(
            subject="OTP for Social account email verification",
            recipients=[[r["email"]]],
            body=f"<h1>The OTP for Social account email verification is <b>{r['otp']}</b></h1>. <b>The OTP is valid for 10 minutes</b>",
            subtype=MessageType.html,)
        background_tasks.add_task(fm.send_message,message)
        return {"success":True}
    return r

@app.post("/verify")
def verify(token: Token, otp: str):
    return 

@app.post("/login")
def login(user: Login):
    return authenticate_user(user)

@app.post("/get")
def get(token: Token):
    return get_current_user(token.token)

@app.post("/edit")
def edit(token: Token, user: UserBASE):
    return edit_user(token.token, user)

@app.post("/delete")
def delete(token: Token):
    return delete_user(token.token)
