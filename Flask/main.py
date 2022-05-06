from flask import Flask, render_template, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from data import db_session
from data.users import User
from data.chats import Chats
from data.messages import Messages
from data.users_connection import Connection
from pyngrok import ngrok
import eventlet
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
import datetime


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

https_tunnel = ngrok.connect(5000, bind_tls=True).public_url

print(https_tunnel)


@app.route("/")
def main():
    return render_template("start.html")

@app.route("/profil")
def profil():
    return render_template("profil.html")

@app.route("/chat")
def chat():
    db_sess = db_session.create_session()
    rooms = db_sess.query(Connection).all()
    info = [(i.id_user, i.id_chat) for i in rooms]
    
    return render_template("chat.html", address=https_tunnel, chat=info)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", address=https_tunnel, form=form, message="Пароли не совпадают")
        
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("register.html", address=https_tunnel, form=form, message="Такой пользователь уже есть")
        
        user = User(
            name = form.name.data,
            about = form.about.data,
            email = form.email.data 
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=form.remember_me.data)
        return redirect("/chat")
    return render_template("register.html", address=https_tunnel, form=form) 


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/chat")
        return render_template("login.html", message="Неправильный логин или пароль", form=form)
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@socketio.on("message")
def handle_message(json):
    emit("message", {"message": json["message"], "name": json["name"]}, to=json["room"])
    print(json)


@socketio.on("create_chat")
def add_create_chat(json):
    db_sess = db_session.create_session()
    chat = Chats()
    db_sess.add(chat)
    db_sess.commit()

    name = json["name"]
    join_room(chat.id)
    emit("chat_created", {"id": chat.id})


@socketio.on("join_chat")
def join_chat(json):
    db_sess = db_session.create_session()
    chat = db_sess.query(Chats).filter(Chats.id == json["id"]).first()

    if chat:
        join_room(json["id"])
    
    conn = db_sess.query(Connection).filter(Connection.id_user == json["user_id"], Connection.id_chat == json["id"]).first()
    if conn is None and chat:
        connection = Connection (
            id_chat = json["id"],
            id_user = json["user_id"]
        )
        db_sess.add(connection)
        db_sess.commit()



@socketio.on("in_room")
def in_room(json):
    join_room(json["room_id"])
    emit("change_room", {"room": json["room_id"]})
    emit("message", {"message": "Пользователь присоединился", "name": json["name"]}, to=json["room_id"], broadcast=True)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    socketio.run(app)
    eventlet.monkey_patch()

