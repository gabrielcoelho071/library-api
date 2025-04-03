from flask import Flask, render_template, redirect, url_for
from models import *
import sqlalchemy

app = Flask(__name__)


app.config['SECRET_KEY'] = 'vc_senha_sua_protecao'

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template("index.html")

app.run(debug=True)