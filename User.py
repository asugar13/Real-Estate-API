from datetime import datetime
from flask import Response, jsonify 
from bson import json_util  
import bcrypt
import re


class User:
    def __init__(self, username, password, first_name=None, last_name=None, birthdate=None):
        if len(username)>30:
            raise ValueError("Username can't be over 30 characters")
        else:
            self.username = username
        if password is not None:    
            if re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",str(password)):
                self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))
            else:
                raise ValueError("Password needs minimum eight characters, at least one letter and one number")
        
        self.first_name= first_name
        if self.first_name is not None:
            if len(self.first_name)>15:
                raise ValueError("First name can't be over 15 characters")
        self.last_name = last_name
        if self.last_name is not None:
            if len(self.last_name)>20:
                raise ValueError("Last name can't be over 20 characters")
            
            
        self.birthdate = birthdate
        if self.birthdate is not None:
            try:
                self.birthdate = datetime.strptime(birthdate, '%d/%m/%Y')
            except ValueError:
                raise ValueError("Birthdate must be in DD/MM/YYYY format") 
        
        
    def sign_up(self, mongo):    
        check_user = mongo.db.users.find({"username": self.username})
        if check_user.count() == 0:
            user_id = mongo.db.users.insert({"username": self.username,
                                        "password": self.password, "first_name": self.first_name,
                                        "last_name": self.last_name,
                                        "birthdate": self.birthdate})  
            new_user = mongo.db.users.find_one({"_id": user_id}, {"password": False}) 
            result = {"user": new_user['username'] + " registered successfully"}
            return jsonify({'result' : result})
        
        else:
            return "username already exists!"     
        
    def edit_profile(self, mongo):
        updating_user = mongo.db.users.find_one_and_update({"username": self.username},
                                                                    {"$set":
                                                                    {"first_name":self.first_name,
                                                                    "last_name": self.last_name,
                                                                    "birthdate": self.birthdate}
                                                                    })
        updated_user = mongo.db.users.find_one({"username": self.username}, {"password": False, "_id": False})
        updated_user["birthdate"] = str(updated_user["birthdate"]).split(" ")[0]
        response = json_util.dumps(updated_user)
        return Response(response, mimetype='application/json') 