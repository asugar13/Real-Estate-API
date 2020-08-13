from flask import Flask, request, Response, render_template, session, jsonify
from flask_pymongo import PyMongo #mongodb implementation for flask
from bson import json_util
from bson.objectid import ObjectId
from datetime import timedelta
import bcrypt
from User import User

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/realestatedb"
mongo = PyMongo(app)
app.config["SECRET_KEY"] = 'sdn86shbmsdACs'
app.pemanent_session_lifetime = timedelta(minutes=5)      

valid_cities = ["paris", "lyon", "bruxelles", "marseille", "montreal"]
valid_types = ["loft", "condo", "apartment", "house", "mansion"]

#On GET, returns a template with API docs
#On POST, you can sign in and create a session
@app.route("/", methods=["POST", "GET"])
def root_handler():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST": 
        
        username = request.form["username"]
        password = request.form["password"]
        user = mongo.db.users.find_one({"username": username})
        
        if user:   
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                #session.permanent = True
                session["username"] = username
                return "Logged in successfully"
        else:
            return "username not found in the Database" 
        
#On POST, signs you up to the DB
@app.route("/signup", methods=["POST"])
def signup_handler():
    fields = []
    for i in request.form:
        fields.append(i)    
    if "username" in fields and "password" in fields:  
        username = request.form["username"]  
        password = request.form["password"]    
        user = User(username, password)
        return user.sign_up(mongo) 
    else:
        return "You need to specify username and password!"        
            
#On GET, it shows you your profile.
#On POST, you can edit your profile (first name, last name, birthdate)
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
                
            if "last_name" in fields:
                last_name = request.form["last_name"]
                
            
            the_user = User(session["username"], None, first_name, last_name,
                            birthdate)
            return the_user.edit_profile(mongo)
            
        elif request.method == "GET":            
            user = mongo.db.users.find_one({"username":session["username"]}, {"password": False, "_id": False})
            user["birthdate"] = str(user["birthdate"]).split(" ")[0]
            response = json_util.dumps(user)
            return Response(response, mimetype='application/json')            
        
    else:
        return "You are not logged in or your session is expired"
        
        
#On GET, returns a list with all your properties
#On POST, you can edit an existing property
@app.route("/myproperties", methods=["GET", "POST"])
def my_properties_handler():
    if "username" in session:
        if request.method == "GET":
            my_properties = mongo.db.properties.find({"owner": session["username"]},{"_id":False})
            response = json_util.dumps(my_properties)
            if response == '[]':
                return "You do not own any properties here"
            
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
                
                description = place["description"]
                place_type = place["type"]
                bedrooms = place["bedrooms"]
                additional_info = place["additional_info"]
                new_name = None
                
                if "description" in fields:
                    description = request.form["description"]
                if "type" in fields:
                    if request.form["type"] in valid_types:
                        place_type = request.form["type"]
                    else:
                        return "type needs to be one of: " + str(valid_types) + " but you entered: " + request.form["type"]
                if "bedrooms" in fields:
                    try:
                        bedrooms = int(request.form["bedrooms"])
                    except ValueError:
                        return "Please enter a valid integer number for bedrooms record!"
                if "additional_info" in fields:
                    additional_info = request.form["additional_info"]
                    
                if "new_name" in fields:
                    new_name = request.form["new_name"]
                
                if new_name:
                    updating_house = mongo.db.properties.find_one_and_update({"owner": session["username"], "city": city, "name": name},
                                                                                                       {"$set":
                                                                                                        {"description":description,
                                                                                                         "name": new_name,
                                                                                                         "type": place_type,
                                                                                                         "bedrooms": bedrooms,
                                                                                                         "additional_info": additional_info}                    
                                                                                                        })
                    updated_place = mongo.db.properties.find({"name": new_name, "city": city, 
                                                               "owner": session["username"]},{"_id": False})                    
                    
                elif not new_name:
                    updating_house = mongo.db.properties.find_one_and_update({"owner": session["username"], "city": city, "name": name},
                                                                                   {"$set":
                                                                                    {"description":description,
                                                                                     "type": place_type,
                                                                                     "bedrooms": bedrooms,
                                                                                     "additional_info": additional_info}
                                                                                    })
                
                    updated_place = mongo.db.properties.find({"name": name, "city": city,
                                                           "owner": session["username"]},{"_id": False})
                response = json_util.dumps(updated_place)
                
                return Response(response, mimetype='application/json')                                         
            else:
                return "You need to specify a city and a name form keys"
    else:
        return "You are not logged in or your session is expired"
    
#On GET, returns a list with all property objects in given city.
#On POST, a user can create a new property.
@app.route('/<id>/properties', methods=["GET", "POST"])  
def city_properties_handler(id):
    if "username" in session:
        entered = id
        id = id.lower()
        if id in valid_cities:        
            if request.method == "GET":
                houses = mongo.db.properties.find({"city": id}, {"_id": False})
                if houses.count() == 0:
                    return "No properties  found in location: " + id
  
                response = json_util.dumps(houses)
                return Response(response, mimetype='application/json')
            
            if request.method == "POST":           
                fields = []
                for i in request.form:
                    fields.append(i)
                    
                if "name" in fields and "bedrooms" in fields:
                    if len(request.form["name"])>30:
                        return "Property name can't be longer than 30 characters"
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
                            if request.form["type"] in valid_types:
                                place_type = request.form["type"]
                            else:
                                return "type needs to be one of: " + str(valid_types) + " but you entered: " + request.form["type"]                            
                                 
                        if "additional_info" in fields:
                            additional_info = request.form["additional_info"]
                            
                        mongo.db.properties.insert({"name": name, "description": description,
                                                "type": place_type, "bedrooms": bedrooms, 
                                                "additional_info": additional_info,
                                                "owner": session["username"],
                                                "city": id})
                        new_place = mongo.db.properties.find({"name": name, "city": id,
                                                                             "owner": session["username"]}, {"_id":False})
                        response = json_util.dumps(new_place)
                        return Response(response, mimetype='application/json')                         
                    else:
                        return "The same house name from the same owner in the same city (" + id + ") exists. Please edit existing house instead"
                else:
                    return "You need to specify name and bedrooms"
        else:
            return "Valid cities are: " + str(valid_cities) + " but you entered " + entered            
    else:
        return "You are not logged in or your session is expired"


#On GET, deletes your session
@app.route('/logout')
def logout_handler():
    session.pop('username', None)
    #return redirect(url_for(''))
    return "Logged out"


#404 status code customer handler
@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        "message": "Resource not found: " + request.url,
        "status": 404
        })
    response.status_code = 404
    return response

if __name__ == '__main__':
    app.run(debug=True)   