from flask import Flask, request, Response, render_template, session, redirect, url_for, jsonify
from flask_pymongo import PyMongo #mongodb implementation for flask
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt  #module to encrypt user passwords

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
def signup_handler():
    fields = []
    for i in request.form:
        fields.append(i)    
    if "username" in fields and "password" in fields:  
        if len(request.form["username"]) < 30 and len(request.form["password"])<30:
            username = request.form["username"]  #write more code to check fields are there
            password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')     #get user name and pw from form data
    #make sure user does not exist
    
            check_user = mongo.db.users.find({"username": username})
            if check_user.count() == 0:
                user_id = mongo.db.users.insert({"username": username,
                                "password": password, "first_name": None, "last_name": None, "birthdate": None})  #save user to database
                new_user = mongo.db.users.find_one({"_id": user_id}) #make sure user was saved
                result = {"user": new_user['username'] + " registered"}
                return jsonify({'result' : result})
            else:
                return "username already exists!"
        else:
            return "Both username and password need to be less than 30 characters"
    else:
        return "You need to specify username and password!"
           
    
@app.route("/", methods=["POST", "GET"])
def root_handler():
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
#On GET, returns a list with all your houses
@app.route("/myhouses", methods=["GET", "POST"])
def my_houses_handler():
    if "username" in session:
        if request.method == "GET":
            my_properties = mongo.db.properties.find({"owner": session["username"]})
            response = json_util.dumps(my_properties)
            return Response(response, mimetype='application/json')
        elif request.method == "POST":
            fields = []
            for i in request.form:
                fields.append(i)            
            if "city" in fields and "name" in fields:
                city = request.form["city"]
                name = request.form["name"]
                place = mongo.db.properties.find_one({"city": city, "name":name})
                if not place:
                    return "Given place name not found in given city for your profile"
                
                print(place)
                description = place["description"]
                place_type = place["type"]
                bedrooms = place["bedrooms"]
                additional_info = place["additional_info"]
                new_name = None
                
                if "description" in fields:
                    description = request.form["description"]
                if "type" in fields:
                    place_type = request.form["type"]
                if "bedrooms" in fields:
                    try:
                        bedrooms = int(request.form["bedrooms"])
                    except ValueError:
                        return "Please enter a valid integer number for bedrooms record!"
                if "additional_info" in fields:
                    additional_info = request.form["additional_info"]
                    
                if "new_name" in fields:
                    new_name = request.form["new_name"]
                
                if new_name: #TODO: FIX THE REDUNDANCY HERE
                    
                    updating_house = mongo.db.properties.find_one_and_update({"owner": session["username"], "city": city, "name": name},
                                                                                                       {"$set":
                                                                                                        {"description":description,
                                                                                                         "name": new_name,
                                                                                                         "type": place_type,
                                                                                                         "bedrooms": bedrooms,
                                                                                                         "additional_info": additional_info}                    
                                                                                                        })
                    updated_place = mongo.db.properties.find({"name": new_name, "city": city, 
                                                               "owner": session["username"]})                    
                    
                elif not new_name:
                    updating_house = mongo.db.properties.find_one_and_update({"owner": session["username"], "city": city, "name": name},
                                                                                   {"$set":
                                                                                    {"description":description,
                                                                                     "type": place_type,
                                                                                     "bedrooms": bedrooms,
                                                                                     "additional_info": additional_info}
                                                                                    })
                
                    updated_place = mongo.db.properties.find({"name": name, "city": city,
                                                           "owner": session["username"]})
                response = json_util.dumps(updated_place)
                return Response(response, mimetype='application/json')                                         
            else:
                return "You need to specify a city and a name form keys"
    else:
        return "You are not logged in or your session is expired"
    
    
#On GET, returns a list with all house objects in given city.
#On POST, a user can create a new house
@app.route('/<id>/houses', methods=["GET", "POST"])  
def city_houses_handler(id):
    if "username" in session:
        if request.method == "GET":
            houses = mongo.db.properties.find({"city": id})
            if houses.count() == 0:
                return "No houses found in location: " + id
  
            response = json_util.dumps(houses)
            return Response(response, mimetype='application/json')
        if request.method == "POST":           
            fields = []
            for i in request.form:
                fields.append(i)
                
            if "name" in fields and "bedrooms" in fields:
                if len(request.form["name"])>30:
                    return "House name can't be longer than 30 characters"
                else:
                    name = request.form["name"]
                try:
                    bedrooms = int(request.form["bedrooms"])
                except ValueError:
                    return "Please enter a valid integer number for bedrooms record!"                
                
                user = mongo.db.properties.find({"name":name,"city": id,
                                                  "owner": session["username"]})
                
                description = None
                place_type = None
                additional_info = None
                
                if user.count() == 0:
                    
                    if "description" in fields:
                        if len(request.form["description"]) < 300:
                            description = request.form["description"]
                        else:
                            "Description must be less than 300 words"
                        
                    if "type" in fields:
                        place_type = request.form["type"]
                        
                    if "additional_info" in fields:
                        additional_info = request.form["additional_info"]
                        
                    mongo.db.properties.insert({"name": name, "description": description,
                                            "type": place_type, "bedrooms": bedrooms, 
                                            "additional_info": additional_info,
                                            "owner": session["username"],
                                            "city": id})
                    new_place = mongo.db.properties.find({"name": name, "city": id,
                                                                         "owner": session["username"]})
                    response = json_util.dumps(new_place)
                    return Response(response, mimetype='application/json')                         
                else:
                    return "The same house name from the same owner in the same city exists. Please edit existing house instead"
            else:
                return "You need to specify name and bedrooms"  
    return "You are not logged in or your session is expired"

@app.route("/profile", methods=["POST", "GET"])
def profile_handler():
    if "username" in session:        
        if request.method == "POST": 
            
            user = mongo.db.users.find_one({"username": session["username"]})

            first_name = user["first_name"]
            birthdate = user["birthdate"]
            last_name = user["last_name"]
            
            fields = []
            for i in request.form:
                fields.append(i)
                                              
            if "first_name" in fields:
                first_name = request.form["first_name"]
                
            if "birthdate" in fields:
                birthdate = request.form["birthdate"]
                try: 
                    date_time_obj = datetime.strptime(birthdate, '%d/%m/%Y')
                except ValueError:
                    return "Birthdate must be in DD/MM/YYYY format"
                
            if "last_name" in fields:
                last_name = request.form["last_name"]
                
            updating_user = mongo.db.users.find_one_and_update({"username": session["username"]},
                                                               {"$set":
                                                                {"first_name":first_name,
                                                                 "last_name": last_name,
                                                                 "birthdate": birthdate}
                                                                }) 
            updated_user = mongo.db.users.find_one({"username": session["username"]}, {"password": False})
            response = json_util.dumps(updated_user)
            return Response(response, mimetype='application/json')            

        elif request.method == "GET":            
            user = mongo.db.users.find_one({"username":session["username"]}, {"password": False})
            
            response = json_util.dumps(user)
            return Response(response, mimetype='application/json')            
        
    return "You are not logged in or your session is expired"
    
@app.route('/logout')
def logout_handler():
    session.pop('username', None)
    #return redirect(url_for(''))
    return "logged out"

@app.errorhandler(404)
def not_found(error=None):
    #message = {
        #"message": "Resource not found: " + request.url
        #}
    #return message
    response = jsonify({
        "message": "Resource not found: " + request.url,
        "status": 404
        })
    response.status_code = 404
    return response
        


if __name__ == '__main__':
   app.run(debug=True)