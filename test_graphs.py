# import dash
# from dash.dependencies import Input, Output
# import dash_core_components as dcc
# import dash_html_components as html
# from pandas_datareader import data as wb
# from datetime import datetime as dt
#
# app = dash.Dash('Graphs with Python')
#
# app.layout = html.Div([
#     dcc.Dropdown(
#         id='my-dropdown',
#         options=[
#             {'label': 'Coke', 'value': 'KO'},
#             {'label': 'Tesla', 'value': 'TSLA'},
#         ],
#         value='KO'
#     ),
#     dcc.Graph(id='my-graph')
# ], style={'width': '500'})
#
# @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
# def update_graph(selected_dropdown_value):
#     stock = wb.DataReader(selected_dropdown_value, data_source='yahoo', start='2016-1-1')
#     return {
#         'data': [{
#             'x': stock.index,
#             'y': stock.Close
#         }],
#         'layout': {'margin': {'l': 40, 'r': 10, 't':20, 'b': 30}}
#     }
#
#
# if __name__ == '__main__':
#     app.run_server()
#
#
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as wb
from datetime import datetime as dt

app = dash.Dash('Graphs with Python')


x_values = ["uno", "two", "three"]
y_values = [6, 7, 5]


def graph_call():

    app.layout = html.Div([
        dcc.Dropdown(
            id='my-dropdown',
            options=[
                {'label': 'NCoke', 'value': 'KO'},
                {'label': 'NTesla', 'value': 'TSLA'},
            ],
            value='KO'
        ),
        dcc.Graph(id='my-graph')
    ], style={'width': '500'})

    @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        return {
            'data': [{
                'x': x_values,
                'y': y_values
            }],
            'layout': {'margin': {'l': 40, 'r': 10, 't':20, 'b': 30}}
        }

print("hi")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

@app.route('/')
def home():
    # Every render_template has a logged_in variable set.
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route('/logout')
def logout():
    graph_call()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)