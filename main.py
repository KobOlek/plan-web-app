import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from flask_ngrok import run_with_ngrok

from datetime import date
from random import random

from forms import *
from emailSender import EmailSender

app = Flask(__name__)
#run_with_ngrok(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

sender_email = ""
with open("devEmails", "r") as file:
    sender_email = file.read()

sender_password = ""
with open("devEmailPasswords", "r") as file:
    sender_password = file.read()

sender = EmailSender(sender_email, sender_password)

# "sqlite://plans.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:25092008Olek@localhost/plans'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    email = EmailField(validators=[InputRequired()], render_kw={"placeholder":"Email"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register", render_kw={"class": "btn btn-success"})

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username is already taken")



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String())
    user_id = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(), default="#E3651D")
    importance = db.Column(db.String(), default="not important")
    created_time = db.Column(db.String(), default=date.today().strftime("%d.%m.%Y"))
    planned_time = db.Column(db.String(), nullable=False)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('plans', id=user.id))
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('plans', id=new_user.id))

    return render_template("register.html", form=form)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<int:id>/plans", methods=["GET", "POST"])
def plans(id):
    db.get_or_404(User, id)
    if request.method == "POST":
        plan_id = request.form["plan-id"]
        current_plan = Plan.query.filter_by(id=plan_id).first()
        if request.form.get("changing_action") == "Delete":
            db.session.delete(current_plan)
            db.session.commit()

        if request.form.get("changing_action") == "Save":
            current_plan.color = request.form.get("color")
            current_plan.importance = request.form.get("importance")
            db.session.commit()

    plan_list = Plan.query.filter_by(user_id=id).order_by(Plan.id).all()[::-1]
    return render_template("plans.html", id=id, plans=plan_list)

@app.route("/<int:id>/plans/add-plan", methods=["GET", "POST"])
def add_plan(id):
    db.get_or_404(User, id)
    form = AddPlanForm()

    if form.validate_on_submit():
        plan_color = get_color_due_to_importance(form.importance.data)

        plan = Plan(header=form.header.data, description=form.description.data,
                    user_id=id, importance=form.importance.data, color=plan_color,
                    planned_time=f"{form.planned_time_day.data}.{form.planned_time_month.data}.{date.today().year}")
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("plans", id=id))

    plan_list = Plan.query.filter_by(user_id=id).order_by(Plan.id).all()[::-1]
    return render_template("add-plan.html", id=id, form=form, plans=plan_list,
                           color=f"rgb({random()*255}, {random()*255}, {random()*255})")

@app.route("/<int:id>/edit-plan/<int:plan_id>", methods=["GET", "POST"])
def edit_plan(id: int, plan_id: int):
    db.get_or_404(User, id)
    db.get_or_404(Plan, plan_id)

    plan = Plan.query.filter_by(id=plan_id).first()
    form = EditPlanForm()

    if form.validate_on_submit():
        plan.header = form.header.data
        plan.description = form.description.data
        plan.importance = form.importance.data
        plan.planned_time = f"{form.planned_time_day.data}.{form.planned_time_month.data}"
        plan.color = get_color_due_to_importance(plan.importance)
        db.session.commit()
        return redirect(url_for("plans", id=id))

    form.header.data = plan.header
    form.description.data = plan.description
    form.importance.data = plan.importance
    form.planned_time_day.data = int(plan.planned_time.split(".")[0])
    form.planned_time_month.data = plan.planned_time.split(".")[1]

    return render_template("edit-plan.html", user_id=id, plan_id=id, plan=plan, form=form)


def get_color_due_to_importance(importance: str) -> str:
    match importance:
        case "important":
            plan_color = "#f70c5d"
        case "very important":
            plan_color = "#f70c0c"
        case _:
            plan_color = "#E3651D"
    return plan_color

def is_today(dateStr):
    dateObj = datetime.datetime.strptime(dateStr, '%d.%m.%Y').date()
    today = datetime.datetime.now().date()
    return dateObj == today

def send_reminding():
    global sender
    today_date = datetime.date.today().strftime("%d.%m.%Y")

    plans = Plan.query.all()
    for plan in plans:
        try:
            if is_today(plan.planned_time):
                current_user = User.query.filter_by(id=plan.user_id).first()
                sender.send_email(f"You had to have done {plan.importance} plan today!", current_user.email, f"Reminding {today_date}")
        except:
            print("Not correct format of date")

with app.app_context():
    send_reminding()

if __name__ == "__main__":
    app.run()
