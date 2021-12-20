from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
from flask_app.models import user

from flask_app import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Game:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.description = data['description']
        self.year_released = data['year_released']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        self.users = []
    
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM games;"
        results = connectToMySQL('#').query_db(query)
        games = []
        for game in results:
            games.append( cls(game) )
        return games
    
    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM games WHERE games.id = %(id)s;"
        recipe_from_db = connectToMySQL('#').query_db(query,data)
        return cls(recipe_from_db[0])
    
    @classmethod
    def save(cls, data ):
        query = "INSERT INTO games ( name , type, description , year_released , created_at, updated_at ) VALUES ( %(name)s , %(type)s, %(description)s , %(year_released)s , %(created_at)s , %(created_at)s );"
        return connectToMySQL('#').query_db( query, data )

    @classmethod
    def created(cls, data):
        query = "INSERT INTO created (user_id, game_id) VALUES (%(user_id)s, %(game_id)s);"
        return connectToMySQL('#').query_db(query,data)

    @classmethod
    def show(cls, data):
        query = "SELECT * FROM games WHERE id = %(id)s;"
        results = connectToMySQL('#').query_db(query, data)
        games = []
        for game in results:
            games.append( cls(game) )
        return games

    @classmethod
    def edit(cls, data):
        query = "UPDATE games SET name=%(name)s, type=%(type)s, description=%(description)s, year_released=%(year_released)s,  updated_at=%(updated_at)s WHERE id = %(id)s;"
        return connectToMySQL('#').query_db( query, data )

    @classmethod
    def destroy(cls, data):
        query = "DELETE FROM games WHERE id = %(id)s;"
        return connectToMySQL('#').query_db( query, data)

    @classmethod
    def destroycreate(cls, data):
        query = "DELETE FROM created WHERE game_id = %(id)s;"
        return connectToMySQL('#').query_db( query, data)


    @classmethod
    def get_game_with_users( cls , data ):
        query = "SELECT * FROM games LEFT JOIN created on created.game_id = games.id LEFT JOIN users ON created.user_id = users.id WHERE games.id = %(id)s;"
        results = connectToMySQL('#').query_db( query , data )
        
        game = cls( results[0] )
        for row_from_db in results:
            
            user_data = {
                "id" : row_from_db["users.id"],
                "first_name" : row_from_db["first_name"],
                "last_name" : row_from_db["last_name"],
                "email" : row_from_db["email"],
                "password" : row_from_db["password"],
                "created_at" : row_from_db["users.created_at"],
                "updated_at" : row_from_db["users.updated_at"]
            }
            game.users.append( user.User( user_data ) )
        return game
        
    @staticmethod
    def validate_game(game):
        is_valid = True
        if len(game['name']) < 1:
            flash("Name Required.")
            is_valid = False
        if len(game['type']) < 1:
            flash("Type Required.")
            is_valid = False
        if len(game['description']) < 1:
            flash("Description Required.")
            is_valid = False
        
        if len(game['year_released']) < 1:
            flash("Date Released must be over 1 character.")
            is_valid = False
        return is_valid

    @classmethod
    def get_users_games(cls):
        query = "SELECT * FROM games LEFT JOIN created ON created.game_id = games.id JOIN users ON created.user_id = users.id;"
        results = connectToMySQL('#').query_db(query)
        users_games = []
        for row in results:
            new_game = True
            user_data = {
                "id" : row['users.id'],
                "first_name" : row['first_name'],
                "last_name" : row['last_name'],
                "email" : row['email'],
                "password" : row['password'],
                "created_at" : row['users.created_at'],
                "updated_at" : row['users.updated_at']
            }
            if len(users_games) >0 and users_games[len(users_games) - 1].id == row["id"]:
                user_obj = user.User(user_data)
                users_games[len(users_games) - 1].users.append(user_obj)
                new_game = False
            if new_game:
                game = cls(row)
                if row['users.id'] is not None:
                    game.users.append(user.User(user_data))
                users_games.append(game)
        return users_games