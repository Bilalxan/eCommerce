from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
bootstrap = Bootstrap5(app)

# Login Setup
login_manager = LoginManager()
login_manager.init_app(app)

# DB Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment.db'
db = SQLAlchemy(app)


# db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


#
# TODO: Create a User table for all your registered users.
class User(UserMixin, db.Model):
    __tablename__ = "blog users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(
                password=form.password.data, method='pbkdf2', salt_length=8
            )
            new_user = User(
                email=form.email.data,
                password=hashed_password,
                username=form.username.data,
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_page'))
        except:
            flash('You have already registered, login instead!')
            return redirect(url_for('login_page'))
    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.username == username))
        user = result.scalar()
        try:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Password is incorrect. Please try!")
                return redirect(url_for("login_page"))
        except AttributeError:
            flash("The email doesn't exist, register first!")
            return redirect(url_for("register"))
    return render_template('login.html', form=form, current_user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/payment')
def payment_page():
    return render_template('payment.html')


if __name__ == '__main__':
    app.run(debug=True)
