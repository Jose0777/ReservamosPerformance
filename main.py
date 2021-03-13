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
from operation_data_engineer import question_operation_engineer
from strategist_data_engineer import question_strategist_engineer
from management_data_engineer import question_management_engineer
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
    C1 = db.Column(db.Float)
    C2 = db.Column(db.Float)
    C3 = db.Column(db.Float)
    C4 = db.Column(db.Float)
    C5 = db.Column(db.Float)
    C6 = db.Column(db.Float)
    C7 = db.Column(db.Float)
    C8 = db.Column(db.Float)
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

@app.route('/secrets')
@login_required
def questions_by_area():
    return render_template("strategist.html", email=current_user.email, name=current_user.name,
                           questions_operation=question_operation, questions_strategist=question_strategist,
                           questions_management=question_management, questions_operation_engineer=question_operation_engineer,
                           questions_strategist_engineer=question_strategist_engineer, user=current_user.email,
                           questions_management_engineer=question_management_engineer, people=people, logged_in=True)


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
        name=(request.form.get("name")).title(),
        password = hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database
        login_user(new_user)

        return redirect(url_for("questions_by_area"))

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


@app.route("/evaluation", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        form = request.form
        name_evaluated = form['name_person']
        for name in people:
            if people[name]['name'] == name_evaluated:
                category = people[name]['category']
                area = people[name]['area']
                leader_person = people[name]['leader']
            if people[name]['email'] == current_user.email:
                name_evaluator = people[name]['name']
        return render_template("questionsform.html", email=current_user.email, name=current_user.name,
                               questions_operation=question_operation, questions_strategist=question_strategist,
                               questions_management=question_management, questions_operation_engineer=question_operation_engineer,
                               questions_strategist_engineer=question_strategist_engineer, questions_management_engineer=question_management_engineer, people=people, logged_in=True,
                               name_evaluated=name_evaluated, category=category, area=area, leader_person=leader_person,
                               name_evaluator=name_evaluator, user=current_user.email)


@app.route("/", methods=["GET", "POST"])
def submitted():
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
            if people[index]['name'] == person_evaluated:
                ind_ = index # indice de persona evaluada
                leader_person = people[index]['leader']
            if people[index]['email'] == current_user.email:
                evaluator_name = people[index]['name']
        if ind_:
            print(ind_)
            if people[ind_]['area'] != "engineer":
                area_person = "not_engineer"
                if people[ind_]['category'] == "Operation":
                    questions = question_operation
                elif people[ind_]['category'] == "Strategist":
                    questions = question_strategist
                elif people[ind_]['category'] == "Direction":
                    questions = question_management
            if people[ind_]['area'] == "engineer":
                area_person = "engineer"
                if people[ind_]['category'] == "Operation":
                    questions = question_operation_engineer
                elif people[ind_]['category'] == "Strategist":
                    questions = question_strategist_engineer
                elif people[ind_]['category'] == "Direction":
                    questions = question_management_engineer
            #print(questions)
            # considera un else break...
            for q_ in range(0, len(questions)):
                if q_ % 3 == 0:
                    quest = questions[q_]["category"] # Compromiso Org., Pensamiento Anal.
                    categories.append(quest)
        if area_person == "not_engineer":
            c1 = None
            c2 = None
            c3 = None
            c4 = None
            c5 = None
            c6 = None
            c7 = None
            c8 = None
            # answer of the questions ans can be (0 -> 4)  añadi al final persona evaluada cómo afecta?
            print(leader_person+" lead")
            if evaluator_name == leader_person:
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
                    q1 = None
                if form['Q2'] == "":
                    q2 = None
                if form['Q3'] == "":
                    q3 = None
                if form['Q4'] == "":
                    q4 = None
            if evaluator_name != leader_person:
                for index in range(1, len(form)):
                    ind = "a"+str(index)
                    values.append(int(form[ind]))
                q1 = None
                q2 = None
                q3 = None
                q4 = None
        if area_person == "engineer":
            q1 = None
            q2 = None
            q3 = None
            q4 = None
            if evaluator_name == leader_person:
                for index in range(1, len(form)-8):
                    ind = "a"+str(index)
                    values.append(int(form[ind]))
                    #
                c1 = form['C1']
                c2 = form['C2']
                c3 = form['C3']
                c4 = form['C4']
                c5 = form['C5']
                c6 = form['C6']
                c7 = form['C7']
                c8 = form['C8']
                if form['C1'] == "":
                    c1 = None
                if form['C2'] == "":
                    c2 = None
                if form['C3'] == "":
                    c3 = None
                if form['C4'] == "":
                    c4 = None
                if form['C5'] == "":
                    c5 = None
                if form['C6'] == "":
                    c6 = None
                if form['C7'] == "":
                    c7 = None
                if form['C8'] == "":
                    c8 = None
            if evaluator_name != leader_person:
                for index in range(1, len(form)):
                    ind = "a" + str(index)
                    values.append(int(form[ind]))
                c1 = None
                c2 = None
                c3 = None
                c4 = None
                c5 = None
                c6 = None
                c7 = None
                c8 = None
        tz = pytz.timezone('America/Monterrey')
        monterrey_now = datetime.now(tz)
        new_answers = Team(
            evaluator=evaluator_name,
            evaluated_person=person_evaluated,
            email_evaluator=current_user.email,
            answers=str(values),
            Q1=q1,
            Q2=q2,
            Q3=q3,
            Q4=q4,
            C1=c1,
            C2=c2,
            C3=c3,
            C4=c4,
            C5=c5,
            C6=c6,
            C7=c7,
            C8=c8,
            category_answer=str(categories),
            answer_date=monterrey_now,
            leader=leader_person
        )
        db.session.add(new_answers)
        db.session.commit()
        #get_answer_database()
    return redirect(url_for('questions_by_area'))


@app.route('/report')
@login_required
def answer_database():
    answers_database = db.session.query(Team).all()
    names = []
    for n_options in answers_database:
        names.append(n_options.evaluated_person)
    my_name_list = list(set(names)) # get list with no duplicated names
    return render_template('link_Results.html', logged_in=current_user.is_authenticated, user=current_user.email,
                           options=my_name_list)


@app.route('/download', methods=["GET", "POST"])
@login_required
def get_answer_database():
    if request.method == "POST":
        form = request.form
        chosen_person = form['person_id']
        print(chosen_person)
        answers_database = db.session.query(Team).all()
        stored_answers = [] # answers of team evaluation
        self_stored_answers = [] # answers of autoevaluation
        # evalua cuando los resultados de cuando la persona aparece en la db
        for person in answers_database:
            if chosen_person == person.evaluated_person and person.evaluator == chosen_person:
                self_ans = person.answers
                self_ans = self_ans.replace(' ', '')
                self_ans = self_ans.replace("'", "")
                self_ans = self_ans.replace("[", "")
                self_ans = self_ans.replace("]", "")
                self_ans = self_ans.split(",") # convert the string to an array
                # array of number for answer:
                self_ans_array = [int(numeric) for numeric in self_ans] #convert to an array of numbers
                # conversion of answer to percentage:
                self_ans_conversion = []
                for n in range(0, len(self_ans_array)):
                    self_ans_ = self_ans_array[n]
                    if self_ans_ == 1:
                        self_ans_ = 25
                    elif self_ans_ == 2:
                        self_ans_ = 50
                    elif self_ans_ == 3:
                        self_ans_ = 75
                    elif self_ans_ == 4:
                        self_ans_ = 100
                    self_ans_conversion.append(self_ans_)
                self_stored_answers.append(self_ans_conversion)

            if chosen_person == person.evaluated_person and person.evaluator != chosen_person:
                val_okrs = []
                val_okrs.append(person.Q1)
                val_okrs.append(person.Q2)
                val_okrs.append(person.Q3)
                val_okrs.append(person.Q4)
                val_okrs.append(person.C1)
                val_okrs.append(person.C2)
                val_okrs.append(person.C3)
                val_okrs.append(person.C4)
                val_okrs.append(person.C5)
                val_okrs.append(person.C6)
                val_okrs.append(person.C7)
                val_okrs.append(person.C8)
                result_mean_okrs = np.average([x for x in val_okrs if x != None])
                #print(okrs_array+" OKRS")
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
        print(self_stored_answers)
        # average of array: https://stackoverflow.com/questions/2153444/python-finding-average-of-a-nested-list/2157646
        answers_mean = np.mean(stored_answers, axis=0)
        self_answers_mean = np.mean(self_stored_answers, axis=0)
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

        # Resultados:
        result_okr = np.round(result_mean_okrs*0.7, decimals=2)
        self_evaluation = np.round(np.mean(self_answers_mean*0.3), decimals=2)
        print(self_evaluation)
        team_evaluation = np.round(np.mean(x_ans*0.3), decimals=2) # Evaluación del team Competencias
        total_evaluation = team_evaluation + result_okr
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
        return render_template('download.html', logged_in=current_user.is_authenticated, person=chosen_person,
                               options=answers_database, x_values=x_ans, y_values=y_ans, team_evaluation=team_evaluation,
                               result_okr=result_okr, self_evaluation=self_evaluation, total_evaluation=total_evaluation,
                               user=current_user.email,)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)