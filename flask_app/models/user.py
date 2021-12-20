from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
from flask_app.models import game
from flask_app.models.game import Game
from flask_app import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        self.games = []
    
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL('#').query_db(query)
        users = []
        for user in results:
            users.append( cls(user) )
        return users
    
    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM users WHERE users.id = %(id)s;"
        user_from_db = connectToMySQL('#').query_db(query,data)
        return cls(user_from_db[0])
    
    @classmethod
    def get_oneinfo(cls,data):
        query = "SELECT * FROM users WHERE users.id = %(id)s;"
        user_from_db = connectToMySQL('#').query_db(query,data)
        return cls(user_from_db[0])
    
    @classmethod
    def save(cls, data ):
        query = "INSERT INTO users ( first_name , last_name , email , password, created_at, updated_at ) VALUES ( %(fname)s , %(lname)s , %(email)s , %(password)s, NOW() , NOW() );"
        return connectToMySQL('#').query_db( query, data )

    @classmethod
    def show(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL('#').query_db(query, data)
        users = []
        for user in results:
            users.append( cls(user) )
        return users

    @classmethod
    def edit(cls, data):
        query = "UPDATE users SET first_name=%(fname)s, last_name=%(lname)s, email=%(email)s, updated_at=NOW() WHERE id = %(id)s;"
        return connectToMySQL('#').query_db( query, data )

    @classmethod
    def destroy(cls, data):
        query = "DELETE FROM users WHERE id = %(id)s;"
        return connectToMySQL('#').query_db( query, data)

    @staticmethod
    def validate_user( user ):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_name(user):
        is_valid = True
        if len(user['fname']) < 2:
            flash("First name must be at least 3 characters.")
            is_valid = False
        if len(user['lname']) < 2:
            flash("Last name must be at least 3 characters.")
            is_valid = False
        return is_valid

    @staticmethod
    def password_match(user):
        is_valid = True
        if user["password"] != user["confirm"]:
            flash("Passwords must match.")
            is_valid = False
        return is_valid

    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL("#").query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_user_with_games( cls , data ):
        query = "SELECT * FROM users LEFT JOIN created on created.user_id = users.id LEFT JOIN games ON created.game_id = games.id WHERE users.id = %(id)s;"
        results = connectToMySQL('#').query_db( query , data )
        
        user = cls( results[0] )
        for row_from_db in results:
            
            recipe_data = {
                "id" : row_from_db["games.id"],
                "name" : row_from_db["name"],
                "type" : row_from_db["type"],
                "description" : row_from_db["description"],
                "year_released" : row_from_db["year_released"],
                "created_at" : row_from_db["games.created_at"],
                "updated_at" : row_from_db["games.updated_at"]
            }
            user.games.append( game.Game( recipe_data ) )
        return user

    @classmethod
    def get_users_games(cls):
        query = "SELECT * FROM users LEFT JOIN created ON created.user_id = users.id JOIN games ON created.game_id = games.id;"
        users_games_db = connectToMySQL('#').query_db( query)

        users_games = []

        for row in users_games_db:
            user_instance = User(row)
            game_data = {
                "id" : row["games.id"],
                "name" : row["name"],
                "type" : row["type"],
                "description" : row["description"],
                "year_released" : row["year_released"],
                "created_at" : row["games.created_at"],
                "updated_at" : row["games.updated_at"]
            }
            user_instance.game = Game(game_data)
            users_games.append(user_instance)
        return users_games

