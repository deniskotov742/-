from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

database = SQLAlchemy(app)
locked_flag = True

class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(100), unique=True)
    psw = database.Column(database.String(100), nullable=True)
    date = database.Column(database.DateTime, default=datetime.utcnow)

    hook = database.relationship('Profiles', backref='users', uselist=False)

    def __repr__(self):
        return f'<User {self.id}>'

class Profiles(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=True)
    old = database.Column(database.Integer)
    city = database.Column(database.String(100))

    user_id = database.Column(database.Integer, database.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Profile {self.id}>'

@app.route('/')

def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            #user = Users(email=request.form['email'], psw=request.form['psw'])
            user = Users()
            user.email = request.form['email']
            user.psw = request.form['psw']
            database.session.add(user)
            database.session.flush()

            #profile = Profiles(name=request.form['name'], old=request.form['old'], city=request.form['city'], user_id=user.id)
            profile = Profiles()
            profile.name = request.form['name']
            profile.old = request.form['old']
            profile.city = request.form['city']
            
            database.session.add(profile)
            database.session.commit()

        except:
            database.session.rollback()
            print('Ошибка записи в базу данных')

    return render_template('register.html')

@app.route('/locked')
def locked():
    global locked_flag
    if locked_flag == False:
        return render_template('locked.html')
    else:
        return redirect('/register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email'], psw=request.form['psw']).first()
        if user:
            global locked_flag
            locked_flag = False
            return redirect('/locked')

    return render_template('login.html')

with app.app_context():
    database.create_all()

if __name__ == '__main__':

    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/register', 'register', register)
    app.add_url_rule('/login', 'login', login)
    app.add_url_rule('/locked', 'locked', locked)
    app.run(host='0.0.0.0', port=80)