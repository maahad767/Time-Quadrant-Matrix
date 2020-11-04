from flask import Flask, request, redirect, render_template, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__) 
app.secret_key = 'ILoveCS50ButIloveProphetMuhammadSallallahuAlaihiWasallamMore'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timematrix.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True
app.permanent_session_lifetime = timedelta(days=7)

db = SQLAlchemy(app)

# decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user-email' in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# models
class User(db.Model):
    __tablename__ = 'user'
    _id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    # address = db.relationship("Address", backref='user', lazy=True, cascade="all, delete",
    #     passive_deletes=True)
    # address = db.Column(db.Integer, unique=True)
    password = db.Column(db.Text, nullable=False)
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        
    def __repr__(self):
        return self.email


class Address(db.Model):
    __tablename__ = 'address'
    _id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user._id', ondelete='CASCADE'), nullable=False)
    addr1 = db.Column(db.String(255), nullable=False)
    addr2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    def __init__(self, user_id, addr1, addr2, city, state, zipcode, country):
        self.uid = user_id
        self.addr1 = addr1
        self.addr2 = addr2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.country = country

    def __repr__(self):
        if self.addr2:
            return f"{self.addr2}, {self.addr1}, {self.city}, {self.state}, {self.country}"
        return f"{self.addr1}, {self.city}, {self.state}, {self.country}"


class Task(db.Model):
    __tablename__ = 'task'
    _id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user._id', ondelete='CASCADE'), nullable=False)
    task_text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String, nullable=False)
    important = db.Column(db.Boolean, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(self, owner, task_text, deadline, category='other', important=True):
        self.owner = owner
        self.task_text = task_text
        self.created = datetime.now()
        self.deadline = deadline
        self.category = category
        self.important = important
        self.active = True

        
# views
@app.route('/')
def index():
    if 'user-email' in session:
        return render_template('index.html')
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            user = User.query.filter_by(email=email).first()
            password_hash = user.password

            # verify username and password match
            if sha256_crypt.verify(password, password_hash):
                session["logged_in"] = True
                session["user-firstname"] = user.first_name
                session["user-email"] = email
                flash("You've successfully logged in!", category='success')
                return redirect(url_for('index'))
        flash('Username/password Invalid', category='danger')
        return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You've been logged out!", category='warning')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user-email' in session:
        flash("You're already registered!!", category='warning')
        return redirect(url_for('index'))
    if request.method == 'POST':
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        addr1 = request.form.get('address1')
        addr2 = request.form.get('address2')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zip')
        country = 'Bangladesh'
        if not addr2:
                addr2 = ""
        if first_name and last_name and email and password and addr1 and city and state and zipcode and country:
            if User.query.filter_by(email=email).first():
                flash("Email is already registred!", category='warning')
                return render_template('register.html')

            password_hash = sha256_crypt.hash(password)
            user = User(first_name=first_name, last_name=last_name, email=email, password=password_hash)
            db.session.add(user)
            db.session.commit()
            address = Address(user._id, addr1=addr1, addr2=addr2, city=city, state=state, zipcode=zipcode, country=country)
            db.session.add(address)
            db.session.commit()
            flash("You've successfully registred!", category='success')
            session["logged_in"] = True
            session["user-firstname"] = user.first_name
            session["user-email"] = email
            return redirect(url_for('index'))
        
        flash("Unknown Error Occured", category='danger')
    return render_template('register.html')

@app.route('/addtask', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST' and session['user-email']:
        task_text = request.form.get('task-text')
        deadline = datetime.strptime(request.form.get('datetime'), '%Y-%m-%dT%H:%M')
        category = request.form.get('category')
        importance = (True if request.form.get('importance') == 'high' else False)
        owner = User.query.filter_by(email=session['user-email']).first()._id
        task = Task(owner, task_text, deadline, category, importance)
        db.session.add(task)
        db.session.commit()
        flash('Your task was added successfully!', category="success")
        if 'add' in request.form:
            return redirect(url_for('index'))
        elif 'addRecur' in request.form:
            return render_template('add_task.html')
        
    return render_template('add_task.html')

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        if 'complete' in request.form:
            _id = request.form['complete']
            task = Task.query.get(_id)
            task.active = False
            db.session.commit()
        elif 'delete' in request.form:
            _id = request.form['delete']
            task = Task.query.get(_id)
            db.session.delete(task)
            db.session.commit()

    # get all tasks
    owner_id = User.query.filter_by(email=session['user-email']).first()._id
    all_tasks = Task.query.filter_by(owner=owner_id, active=True).order_by(db.desc('created')).all()

    return render_template('all_tasks.html', tasks=all_tasks)


@app.route('/urgent-important')
@login_required
def urgent_important():
    if request.method == 'POST':
        if 'complete' in request.form:
            _id = request.form['complete']
            task = Task.query.get(_id)
            task.active = False
            db.session.commit()
        elif 'delete' in request.form:
            _id = request.form['delete']
            task = Task.query.get(_id)
            db.session.delete(task)
            db.session.commit()

    owner_id = User.query.filter_by(email=session['user-email']).first()._id
    tasks = Task.query.filter(Task.owner==owner_id, Task.active, Task.important, Task.deadline <= datetime.now()+timedelta(days=7)).order_by(Task.deadline.desc()).all()
    return render_template('urgent_important.html', tasks=tasks)

@app.route('/not-urgent-important')
@login_required
def not_urgent_important():
    if request.method == 'POST':
        if 'complete' in request.form:
            _id = request.form['complete']
            task = Task.query.get(_id)
            task.active = False
            db.session.commit()
        elif 'delete' in request.form:
            _id = request.form['delete']
            task = Task.query.get(_id)
            db.session.delete(task)
            db.session.commit()

    owner_id = User.query.filter_by(email=session['user-email']).first()._id
    tasks = Task.query.filter(Task.owner==owner_id, Task.active, Task.important, Task.deadline >= datetime.now()+timedelta(days=7)).order_by(Task.deadline.desc()).all()
    return render_template('not_urgent_important.html', tasks=tasks)

@app.route('/urgent-not-important')
@login_required
def urgent_not_important():
    if request.method == 'POST':
        if 'complete' in request.form:
            _id = request.form['complete']
            task = Task.query.get(_id)
            task.active = False
            db.session.commit()
        elif 'delete' in request.form:
            _id = request.form['delete']
            task = Task.query.get(_id)
            db.session.delete(task)
            db.session.commit()

    owner_id = User.query.filter_by(email=session['user-email']).first()._id
    tasks = Task.query.filter(Task.owner==owner_id, Task.active, Task.important==False, Task.deadline <= datetime.now()+timedelta(days=7)).order_by(Task.deadline.desc()).all()
    return render_template('urgent_not_important.html', tasks=tasks)

@app.route('/not-urgent-not-important')
@login_required
def not_urgent_not_important():
    if request.method == 'POST':
        if 'complete' in request.form:
            _id = request.form['complete']
            task = Task.query.get(_id)
            task.active = False
            db.session.commit()
        elif 'delete' in request.form:
            _id = request.form['delete']
            task = Task.query.get(_id)
            db.session.delete(task)
            db.session.commit()

    owner_id = User.query.filter_by(email=session['user-email']).first()._id
    tasks = Task.query.filter(Task.owner==owner_id, Task.active, Task.important==False, Task.deadline >= datetime.now()+timedelta(days=7)).order_by(Task.deadline.desc()).all()
    return render_template('not_urgent_not_important.html', tasks=tasks)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500

if __name__ == '__main__':
    db.create_all()
    app.run()