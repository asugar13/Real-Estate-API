from flask import Flask, request, Response, render_template, session, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from datetime import timedelta
from flask_bcrypt import Bcrypt

#from pymongo import MongoClient, IndexModel
#from pymongoext import *


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/realestatedb"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = 'sdn86shbmsdACs'
app.pemanent_session_lifetime = timedelta(minutes=5)

#class User(Model):
    #@classmethod
    #def db(cls):
        #return MongoClient()['realestatedb']

    #__schema__ = DictField(dict(
        #username=StringField(required=True),
        #password=StringField(required=True),
        ##yob=IntField(minimum=1900, maximum=2019)
    #))

    #__indexes__ = [IndexModel('username', unique=True), 'password']
        
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"] 
    password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')     #get user name and pw from form data
    
    user_id = mongo.db.users.insert({"username": username,
                            "password": password})  #save user to database
    new_user = mongo.db.users.find_one({"_id": user_id}) #make sure user was saved
    result = {"user": new_user['username'] + " registered"}
    return jsonify({'result' : result})
           
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    #return redirect(url_for(''))
    return "logged out"
    
@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST": 
        username = request.form["username"]
        password = request.form["password"]
        user = mongo.db.users.find_one({"username": username})
        
        if user:   #if user is in the database so variable is not null
            
            if bcrypt.check_password_hash(user['password'], password):
                session.permanent = True
                session["username"] = username
                return "logged in"
            #return redirect(url_for("profile")) #redirect    
        else:
            return "user does not exist"
    
@app.route('/<id>/houses', methods=["GET"])
def get_city_houses(id):
    if "username" in session:
        houses = mongo.db.realestates.find({"city": id})
        response = json_util.dumps(houses)
        return Response(response, mimetype='application/json')
    return "You are not logged in or your session is expired"

@app.route("/profile", methods=["POST", "GET"])
def profile_handler():
    if "username" in session:        
        if request.method == "POST": 
            
            print(request.form)
            for i in request.form:
                print(i)
            username = request.form["username"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            birthdate = request.form["birthdate"]
            if (request.form["last_name"] and request.form["first_name"] 
                and request.form["username"] and request.form["birthdate"]):
                user = mongo.db.users.find_one({"username": username})
                
                if (user["username"] == session["username"]):
                    
                    updating_user = mongo.db.users.find_one_and_update({"username": username},
                                                                          {"$set":
                                                                           {"first_name":first_name,
                                                                            "last_name": last_name,
                                                                            "birthdate": birthdate}
                                                                           
                                                                           }) 
                    updated_user = mongo.db.users.find_one({"username": username})
                    response = json_util.dumps(updated_user)
                    return Response(response, mimetype='application/json')
                else:
                    return "The user name is not in your session"
        elif request.method == "GET":            
            user = mongo.db.users.find_one({"username":session["username"]})
            
            response = json_util.dumps(user)
            return Response(response, mimetype='application/json')            
            
                                           
        
        
    return "You are not logged in or your session is expired"

if __name__ == '__main__':
   app.run(debug=True)