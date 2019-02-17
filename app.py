from flask import Flask, g, render_template, flash, redirect, url_for, abort
import models
import forms
import logging
from logging.handlers import RotatingFileHandler
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)       # Moramo ubaciti secret key ukoliko zelimo koristiti loginmanager
app.secret_key = 'aebnas,bnarbojnaWRBpibarb!asfdbrbw,.rw,bpwrbWB!'

login_manager = LoginManager()      # Pravimo instancu LoginManager-a
login_manager.init_app(app)
login_manager.login_view = 'login'  # Na neki nacin redirecta na view login

@login_manager.user_loader
def load_user(userid):  # Funkcija koju ce LoginManager koristiti prilikom traganja za postojecim userom
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:     # Iz peewee
        return None

@app.before_request     # Spajanje na bazu prije svakog requesta
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request      # Zatvara bazu poslije svakog requesta
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    app.logger.info('Index')
    return render_template('stream.html', stream=stream)

@app.route('/stream')
@app.route('/stream/<username>')
@login_required
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            app.logger.error('An error 404 occurred')
            abort(404)
        else:
            stream = user.posts.limit(100)
            app.logger.info('Stream')
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
        app.logger.info('User_stream')
    return render_template(template, stream=stream, user=user)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        app.logger.error('An error 404 occurred')
        abort(404)
    app.logger.info('Post')
    return render_template('stream.html', stream=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterFrom()     # Kreiramo formu. Ne treba primati nikakve argumente, nego prima preko POST-a
    if form.validate_on_submit():   # Pokrece validaciju
        flash("You have registered!", "success")
        app.logger.info('Registered new user')
        models.User.create_user(        # Dohvacanje vrijednosti kojima su popunjene forme
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))       # Redirect na index nakon registracije
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            app.logger.warning('Email does not exist')
            flash("Your email or password does not match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You have been logged in.", "success")
                app.logger.info('User has logged in')
                return redirect(url_for('index'))
            else:
                app.logger.warning('Password does not match')
                flash("Your email or password does not match!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "success")
    app.logger.info('A user has logged out')
    return redirect(url_for('index'))

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash("Message posted!", "success")
        app.logger.info('There is a new post')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)   # Pokusava naci usera
    except models.DoesNotExist:
        app.logger.error('An error 404 occurred')
        abort(404)
    else:
        try:
            models.Relationship.create(from_user=g.user._get_current_object(),  # Ako nadje usera, stvara Relationship
                                       to_user=to_user)
        except models.IntegrityError:
            pass
        else:
            flash("You are now following {}!".format(to_user.username), "success")  # Salje poruku
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)   # Opet pokusava naci usera
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(from_user=g.user._get_current_object(),  # Ako nadje usera, brise se Relationship
                                       to_user=to_user).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("You have unfollowed {}!".format(to_user.username), "success")  # Salje poruku
    return redirect(url_for('stream', username=to_user.username))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    handler = RotatingFileHandler('logfile.log', maxBytes=1000, backupCount=5)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()
models.initialize()  # Inicijalizacija funkcije iz modela
try:
    models.User.create_user(username='gogo', email='gogo@gmail.com', password='gogo', admin=True)
except ValueError:
    pass
