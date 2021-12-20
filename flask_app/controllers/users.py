import re
from flask import render_template, redirect, request, session

from flask_app import app

from flask_app.models.user import User
from flask_app.models.game import Game
from flask import flash
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/register', methods=["POST"])
def create_user():
    if not User.validate_name(request.form):
        return redirect('/')
    if not User.validate_user(request.form):
        return redirect('/')
    data = { "email" : request.form["email"] }

    user_in_db = User.get_by_email(data)
    if user_in_db:
        flash("Email in use")
        return redirect("/")
    if not User.password_match(request.form):
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
        
    data = {
        "fname": request.form["fname"],
        "lname" : request.form["lname"],
        "email" : request.form["email"],
        "username" : request.form["password"],
        "password" : pw_hash
    }
    

    user_id = User.save(data)
    session["user"] = user_id
    return redirect("/dashboard")

@app.route("/new/game")
def new():
    if "user" in session:
        data = { "id": session["user"]}
        
        return render_template("new.html", user = User.get_one(data))
    return redirect("/")

@app.route("/games/create", methods=["POST"])
def creategame():
    if not Game.validate_game(request.form):
        return redirect("/new/game")
    data = {
        "name":request.form['name'],
        "type":request.form['type'],
        "description": request.form['description'],
        "year_released": request.form['year_released'],
        "created_at" : request.form["created_at"]
    }
    
    game_id = Game.save(data)
    data = {"user_id" : session["user"],
            "game_id": game_id,}
    Game.created(data)
    return redirect('/dashboard')

@app.route("/login", methods=["POST"])
def login():
    # see if the username provided exists in the database
    data = { "email" : request.form["email"] }
    user_in_db = User.get_by_email(data)
    # user is not registered in the db
    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password")
        return redirect('/')
    session['user'] = user_in_db.id
    print(session['user'])
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    
    if "user" in session:
        data = {"id" : session["user"]}
        print(data)
        user = User.get_one(data)
        games = Game.get_all()
        all_games = User.get_users_games()
        my_games = Game.get_users_games()
        return render_template("dashboard.html", user = user, all_games=all_games, games=games,my_games=my_games)

    return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/destroy/<int:game_id>')
def delete(game_id):
    data = {
        'id': game_id,
    }
    Game.destroy(data)
    Game.destroycreate(data)
    return redirect('/dashboard')

@app.route('/show/<int:game_id>')
def show_game(game_id):
    data = {
        'id': game_id
    }
    data2 = {
        "id" : session["user"]
    }
    return render_template("show_details.html", game = Game.get_one(data),all_users=User.get_all(),user= User.get_one(data2),gamecreator=Game.get_game_with_users(data))

@app.route('/created/<int:game_id>', methods=['POST'])
def created(game_id):
    data = {"game_id": game_id,
            "user_id": request.form['user_id']
            }
    Game.created(data)
    return redirect (f"/show/{game_id}")



@app.route("/edit/<int:game_id>")
def edit_game(game_id):
    if "user" in session:
        data = {"id": game_id}
        games = Game.get_one(data)
        data2 = {
        "id" : session["user"]
        }
        user = User.get_one(data2)
        return render_template("edit.html", games=games, user=user)
    return ("/")

@app.route('/update/<int:game_id>', methods=['POST'])
def update(game_id):
    id = game_id
    if not Game.validate_game(request.form):
        return redirect(f"/edit/{id}")
    data = {
        "id" : game_id,
        "name":request.form['name'],
        "type":request.form['type'],
        "description": request.form['description'],
        "year_released": request.form['year_released'],
        "updated_at" : request.form["updated_at"]
    }
    Game.edit(data)
    return redirect("/dashboard")

@app.route("/user_details/<user_id>")
def user_details(user_id):
    data = {"id" : session["user"]}
    data2 = {"id": user_id}
    return render_template("user_details.html",  games=Game.get_all(), user = User.get_oneinfo(data2), usergames = User.get_user_with_games(data2), usersession = User.get_one(data))

@app.route('/createdgame/<int:user_id>', methods=['POST'])
def createdgame(user_id):
    data = {"user_id": user_id,
            "game_id": request.form['game_id']
            }
    Game.created(data)
    return redirect (f"/user_details/{user_id}")