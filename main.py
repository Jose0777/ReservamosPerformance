from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_bootstrap import Bootstrap
from wtforms.validators import DataRequired, URL
from bs4 import BeautifulSoup
from people_dictionary import people
from operation_data import question_operation
from strategist_data import question_strategist
from management_data import question_management
from datetime import datetime, timezone
import pytz
from matplotlib import pyplot
import numpy as np

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

# Configuring your Application
# https://flask-login.readthedocs.io/en/latest/#configuring-your-application
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# #CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
# Line below only required once, when creating DB.
# db.create_all()


# #CREATE TABLE IN DB
class Team(db.Model):
    __tablename__ = "team_answers"
    id = db.Column(db.Integer, primary_key=True)
    evaluator = db.Column(db.String(100))
    evaluated_person = db.Column(db.String(100))
    email_evaluator = db.Column(db.String(100), unique=False)
    answers = db.Column(db.String())
    Q1 = db.Column(db.Float)
    Q2 = db.Column(db.Float)
    Q3 = db.Column(db.Float)
    Q4 = db.Column(db.Float)
    category_answer = db.Column(db.String())
    answer_date = db.Column(db.DateTime)
    leader = db.Column(db.String(100))

# Line below only required once, when creating DB.
db.create_all()


@app.route('/')
def home():
    # Every render_template has a logged_in variable set.
    # para que si se borra la base de datos no falle:
    if current_user.is_authenticated:
        print(current_user.email)
        return render_template("index.html", user=current_user.email, logged_in=current_user.is_authenticated)
    else:
        return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get("password"),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
        email=request.form.get("email"),
        name=request.form.get("name"),
        password = hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database
        login_user(new_user)

        return redirect(url_for("login"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered
        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again or register.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Email exists and password correct
        else:
            login_user(user)
            return redirect(url_for('questions_by_area'))

    return render_template("login.html", logged_in=current_user.is_authenticated)
# class NameForm(FlaskForm):
#     evaluated_person = SelectField('Name of the Evaluated person',
#     choices=["☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"], validators=[DataRequired()])


@app.route('/secrets')
@login_required
def questions_by_area():
    return render_template("strategist.html", email=current_user.email, name=current_user.name,
                           questions_operation=question_operation, questions_strategist=question_strategist,
                           questions_management=question_management, people=people, logged_in=True)


@app.route("/home", methods=["GET", "POST"])
def submit():
    print("hola")
    if request.method == "POST":
        #with open("templates/strategist.html") as file:
        #    contents = file.read()
        #soup = BeautifulSoup(contents, "html.parser")
        #print(soup.prettify())
        values = []
        categories = []
        form = request.form
        leader_person = ""
        ind_ = []
        questions = ""
        person_evaluated = str(form['name_person'])
        print(person_evaluated)
        for index in people:
            if people[index]['email'] == current_user.email:
                ind_ = index
        #    if people[index]['name'] == person_evaluated:
        #        leader_person = people[index]['leader']
        if ind_:
            if people[ind_]['category'] == "Operation":
                questions = question_operation
            elif people[ind_]['category'] == "Strategist":
                questions = question_strategist
            elif people[ind_]['category'] == "Direction":
                questions = question_management
            #print(questions)
            # considera un else break...
            for q_ in range(0, len(questions)):
                if q_ % 3 == 0:
                    quest = questions[q_]["category"] # Compromiso Org., Pensamiento Anal.
                    categories.append(quest)
        # answer of the questions ans can be (0 -> 4)
        for index in range(1, len(form)-4):
            ind = "a"+str(index)
            values.append(int(form[ind]))
        # example of working with matrix using numpy:
        # print(np.array(values)*2)
        q1 = form['Q1']
        q2 = form['Q2']
        q3 = form['Q3']
        q4 = form['Q4']
        if form['Q1'] == "":
            q1 = 0
        if form['Q2'] == "":
            q2 = 0
        if form['Q3'] == "":
            q3 = 0
        if form['Q4'] == "":
            q4 = 0
        tz = pytz.timezone('America/Monterrey')
        monterrey_now = datetime.now(tz)
        new_answers = Team(
            evaluator=current_user.name,
            evaluated_person=person_evaluated,
            email_evaluator=current_user.email,
            answers=str(values),
            Q1=q1,
            Q2=q2,
            Q3=q3,
            Q4=q4,
            category_answer=str(categories),
            answer_date=monterrey_now,
            leader=current_user.name#leader_person
        )
        db.session.add(new_answers)
        db.session.commit()
        #get_answer_database()
    return redirect(url_for('home'))


@app.route('/report')
@login_required
def answer_database():
    answers_database = db.session.query(Team).all()
    return render_template('admin_list.html', logged_in=current_user.is_authenticated, user=current_user.email, options=answers_database)


@app.route('/download', methods=["GET", "POST"])
@login_required
def get_answer_database():
    if request.method == "POST":
        form = request.form
        chosen_person = form['person_id']
        print(chosen_person)
        answers_database = db.session.query(Team).all()
        stored_answers = []
        # evalua cuando los resultados de cuando la persona aparece en la db
        for person in answers_database:
            if chosen_person == person.evaluated_person:
                # print(answers_database)
                ans = person.answers
                ans = ans.replace(' ', '')
                ans = ans.replace("'", "")
                ans = ans.replace("[", "")
                ans = ans.replace("]", "")
                ans = ans.split(",") # convert the string to an array
                # array of number for answer:
                ans_array = [int(numeric_string) for numeric_string in ans] #convert to an array of numbers
                # conversion of answer to percentage:
                ans_conversion = []
                for n_ans in range(0, len(ans_array)):
                    ans_ = ans_array[n_ans]
                    if ans_ == 1:
                        ans_ = 25
                    elif ans_ == 2:
                        ans_ = 50
                    elif ans_ == 3:
                        ans_ = 75
                    elif ans_ == 4:
                        ans_ = 100
                    ans_conversion.append(ans_)
                stored_answers.append(ans_conversion)
                category = person.category_answer.split(",")
                category = [s.replace("[", "") for s in category]
                category = [s.replace("]", "") for s in category]
                category = [s.replace("'", "") for s in category]
        print(stored_answers)
        # average of array: https://stackoverflow.com/questions/2153444/python-finding-average-of-a-nested-list/2157646
        answers_mean = np.mean(stored_answers, axis=0)
        # cada 3 respuestas me debe dar una gráfica, entonces hay que promediar cada 3 respuestas:
        print(answers_mean)
        x_ans = []
        for i in range(0, len(answers_mean)):
            if (i+1)%3 == 0:
                elem_mean = np.mean(answers_mean[i-2:i+1])
                x_ans.append(elem_mean) # almacena promed. cada 3 elements (el num de preguntas deben ser múltiplo de 3)
        x_ans = np.round(x_ans, decimals=2)
        print(x_ans)
        # remove the space before and after each element of the category
        for elem in range(0, len(category)):
            category[elem] = category[elem].strip()
        y_ans = category
        print(y_ans)
        #print(answer.Q1)
        #print(answer.Q2)
        #print(type(answer.Q3))
        # x = ["1", "2", "3"]
        # y = [3, 5, 4]
        # colors = ["blue", "red", "purple"]
        # pyplot.title("Performance")
        # pyplot.bar(x, height=y, color=colors, width=0.5)
        # pyplot.ylabel("Percentage")
        # pyplot.savefig("Performance.png")
        # pyplot.show()
        return render_template('download.html', logged_in=current_user.is_authenticated, person=chosen_person, options=answers_database, x_values=x_ans, y_values=y_ans)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)