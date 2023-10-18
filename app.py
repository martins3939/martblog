from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string
from flask_mail import Mail, Message
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///note.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#------flask mail start---------
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#-------flask mail end---------

app.secret_key = os.urandom(234)

db = SQLAlchemy(app)

mail = Mail(app)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    date = db.Column(db.String)
    category = db.Column(db.String)
    title = db.Column(db.String)
    news = db.Column(db.String)


    def __init__(self, name, date, category, title, news):
        self.name = name
        self.date = date
        self.category = category
        self.title = title
        self.news = news

    def __repr__(self):
        return self.name, self.date, self.category, self.title, self.news

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)


    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return self.username, self.password, self.email

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commname = db.Column(db.String)
    comment = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, commname, comment, link):
        self.commname = commname
        self.comment = comment
        self.link = link

    def __repr__(self):
        return self.commname, self.comment, self.link

@app.route('/')
def home():
    fetchnews = News.query.all()
    return render_template('blog.html', fetchnews=fetchnews)

@app.route('/read/<title>', methods=['POST', 'GET'])
def read(title):
    if request.method != 'POST':
        fetchnews = News.query.filter_by(title=title).first()
        fetchcomment = Comment.query.filter_by(link=fetchnews.title).all()
        fetchnews2 = News.query.all()
        return render_template('readmore.html', fetchnews=fetchnews, fetchnews2=fetchnews2, fetchcomment=fetchcomment)
    else:
        commname = request.form['commname']
        comment = request.form['comment']
        link = request.form['link']
        addcomment = Comment(commname=commname, comment=comment, link=link)
        db.session.add(addcomment)
        db.session.commit()

        return redirect(url_for("read", title=title))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        addauth = User(username=username, password=password, email=email)
        db.session.add(addauth)
        db.session.commit()
        return redirect(url_for('login'))

    else:
        return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            fetchUsername = User.query.filter_by(username=username).first()
            fetchPassword = User.query.filter_by(password=password).first()

            if fetchUsername.username == username and fetchPassword.password == password:
                session['logged_in']=True
                return redirect(url_for('show', user=fetchUsername.username))
            else:
                return render_template('login.html', error="invalid username and password combination")
        except:
            try:
                fetchUsername = User.query.filter_by(email=username).first()
                fetchPassword = User.query.filter_by(password=password).first()

                if fetchUsername.email == username and fetchPassword.password == password:
                    session["logged_in"]=True
                    return redirect(url_for('show', user=fetchUsername.username))
                else:
                    return render_template('login.html', error="invalid username and password combination")
            except:
                return render_template('login.html', error="invalid username and password combination")
    else:
        return render_template('login.html')

@app.route('/recover', methods=['POST', 'GET'])
def recover():
    password = string.ascii_uppercase + string.ascii_lowercase + string.digits
    value = ''.join(random.choice(password) for i in range(12))
    if request.method == 'POST':
        email = request.form['email']
        emails = User.query.filter_by(email=email).first()
        pin = str(value)
        fetchpassword = User.query.filter_by(email=email).first()
        try:
            fetchpassword.password = pin
            db.session.commit()
        except:
            return render_template('recover.html', error = "Email not Founds")

        if email == emails.email:
            msg = Message(sender = ('Martins from Martblog', os.getenv('MAIL_USERNAME')), recipients=[email])
            msg.subject = 'Martblog Password Reset'
            msg.body = '''Hey %s, it seems that you forgot your password.

Don't worry about that Martblog will generate a new password for you.


NEW PASSWORD : %s

you can change it anytime at your profile page.


if you didn't request a password reset, please ignore this email and do something fun. it's a nice day. 

''' %(emails.username, pin)
            mail.send(msg)

            return redirect(url_for('login', mesg="Password Recovery Link Successfully Sent to Email"))
        else:
            return render_template('recover.html', error = "Email not Founds")
    else:
        return render_template('recover.html')


@app.route('/show/<user>')
def show(user):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        fetchuser = User.query.filter_by(username=user).first()
        fetchnews = News.query.filter_by(name=user).all()
        return render_template('show.html', fetchuser=fetchuser, fetchnews=fetchnews)

@app.route('/profile/<user>' ,methods=['GET','POST'])
def profile(user):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            username = request.form['username']

            fetchuser = User.query.filter_by(username=user).first()
            fetchuser.username = username
            db.session.commit()
            return render_template('profile.html',fetchuser=fetchuser, msg='username changed')

        else:
            fetchuser = User.query.filter_by(username=user).first()
            return render_template('profile.html', fetchuser=fetchuser)

@app.route('/changepass/<user>' ,methods=['POST'])
def changepass(user):
    oldpass = request.form['oldpass']
    newpass1 = request.form['newpass1']
    newpass2 = request.form['newpass2']

    fetchuser = User.query.filter_by(username=user).first()
    if fetchuser.password == oldpass and newpass1 == newpass2:
        fetchuser.password = newpass1
        db.session.commit()
        return render_template('profile.html',fetchuser=fetchuser, msg='password changed')
    elif oldpass != fetchuser.password:
        return render_template('profile.html',fetchuser=fetchuser, msg='wrong old password')
    elif newpass1 != newpass2:
        return render_template('profile.html',fetchuser=fetchuser, msg="new password don't match")

@app.route('/add/<name>', methods=['POST', 'GET'])
def add(name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            name = request.form['name']
            date = request.form['date']
            category = request.form['category']
            title = request.form['title']
            news = request.form['news']

            addnews = News(name=name, date=date, category=category, title=title, news=news)
            db.session.add(addnews)
            db.session.commit()

            return redirect(url_for("show", user=name))

        else:
            fetchuser = User.query.filter_by(username=name).first()
            return render_template('add.html',fetchuser=fetchuser)

@app.route('/edit/<title>',methods=['GET','POST'])
def edit(title):
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        titles = request.form['title']
        news = request.form['news']

        fetchnews = News.query.filter_by(title=title).first()
        fetchnews.title = titles
        fetchnews.date = date
        fetchnews.category = category
        fetchnews.news = news
        db.session.commit()

        return redirect(url_for('show',user=fetchnews.name))
    else:
        fetchnews = News.query.filter_by(title=title).first()
        return render_template('edit.html',fetchnews=fetchnews)
    
@app.route('/delete/<id>')
def delete(id):
	title = News.query.filter_by(id=id).first()
	db.session.delete(title)
	db.session.commit()

	return redirect(url_for('show',user=title.name))

@app.route('/category/<cat>')
def category(cat):
    if cat == "tech":
        fetchnews = News.query.filter_by(category=cat).all()

        return render_template('tech.html', fetchnews=fetchnews)
    elif cat == "crypto":
        fetchnews = News.query.filter_by(category=cat).all()

        return render_template('crypto.html', fetchnews=fetchnews)
    elif cat == "coding":
        fetchnews = News.query.filter_by(category=cat).all()

        return render_template('coding.html', fetchnews=fetchnews)
    else:
        pass

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host='0.0.0.0')