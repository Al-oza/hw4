from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
#import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
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
    age = db.Column(db.Integer)

    def __repr__(self):
        return "id: {0} | name: {1} | breed: {2} | age: {3}".format(self.dogID, self.dogName, self.dogType, self.age)


class dogsForm(FlaskForm):
    dogID = IntegerField('DogID:', validators=[DataRequired()])
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

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        print('post method')
        form = request.form
        search_value = form['search_string']
        print(search_value)
        search = "%{0}%".format(search_value)
        print(search)
        results = akozakowski_dogsapp.query.filter(or_(akozakowski_dogsapp.dogName.like(search), akozakowski_dogsapp.dogType.like(search))).all()
        print(results)
        return render_template('index.html', dogs = results, pageTitle='Alec\'s Dogs', legend="Search Results")
    else:
        return redirect('/')

@app.route('/delete_dog/<int:dogID>', methods=['GET','POST'])
def delete_dog(dogID):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        obj = akozakowski_dogsapp.query.get_or_404(dogID)
        db.session.delete(obj)
        db.session.commit()
        return redirect("/")
        flash('dog was successfully deleted!')
    else:
        return redirect("/")

@app.route('/get_dog/<int:dogID>', methods=['GET', 'POST'])
def get_dog(dogID):
    obj = akozakowski_dogsapp.query.get_or_404(dogID)
    return render_template('dog.html', form=obj, pageTitle = 'Dog Details', legend="Dog Details")


@app.route('/dog/<int:dogID>/update', methods=['GET', 'POST'])
def update_dog(dogID):
    dog = akozakowski_dogsapp.query.get_or_404(dogID)
    form = dogsForm()

    if form.validate_on_submit():
        dog.dogName = form.dogName.data
        dog.dogType = form.dogType.data
        dog.age = form.age.data
        db.session.commit()
        return redirect(url_for('get_dog', dogID = dog.dogID))

    form.dogID.data = dog.dogID
    form.dogName.data = dog.dogName
    form.dogType.data = dog.dogType
    form.age.data = dog.age
    return render_template('update_dog.html', form=form, pageTitle='Update Dog', legend="Update A Dog")




if __name__ == '__main__':
    app.run(debug==True)
