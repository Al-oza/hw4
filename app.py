from flask import Flask
from flask import render_template, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
#import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

class akozakowski_dogsapp(db.Model):
    dogID = db.Column(db.Integer, primary_key=True)
    dogName = db.Column(db.String(255))
    dogType = db.Column(db.String(255))
    age= db.Column(db.Integer)


class dogsForm(FlaskForm):
    dogName = StringField('Dog Name:', validators=[DataRequired()])
    dogType = StringField('Dog Type:', validators=[DataRequired()])
    age = IntegerField('Dog Age:', validators=[DataRequired()])

@app.route('/')
def index():
    all_dogs= akozakowski_dogsapp.query.all()
    return render_template('index.html', dogs=all_dogs, pageTitle="dogs")

@app.route('/add_dog', methods=['GET','POST'])
def add_dog():
    form = dogsForm()
    if form.validate_on_submit():
        dog = akozakowski_dogsapp(dogName=form.dogName.data, dogType=form.dogType.data, age= form.age.data)
        db.session.add(dog)
        db.session.commit()
        return redirect('/')

    return render_template('add_dog.html', form=form, pageTitle='Add dog')

@app.route('/delete_dog/<int:dogID>', methods=['GET','POST'])
def delete_dog(dogID):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        obj = akozakowski_dogsapp.query.filter_by(dogID=dogID).first()
        db.session.delete(obj)
        db.session.commit()
        flash('dog was successfully deleted!')
        return redirect("/")

    else: #if it's a GET request, send them to the home page
        return redirect("/")


if __name__ == '__main__':
    app.run(debug==True)
