from flask import Flask, request, Response, render_template, session, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from datetime import timedelta



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/realestatedb"
mongo = PyMongo(app)
app.config["SECRET_KEY"] = 'sdn86shbmsdACs'
app.pemanent_session_lifetime = timedelta(minutes=5)

        
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"] 
    password = request.form["password"]     #get user name and pw from form data
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
        
        user = mongo.db.users.find_one({"username": username, "password": password})
        if user:   #if user is in the database so variable is not null
            session.permanent = True
            session["username"] = username
            return "logged in"
            #return redirect(url_for("profile")) #redirect    
    
@app.route('/<id>/houses', methods=["GET"])
def get_city_houses(id):
    if "username" in session:
        houses = mongo.db.realestates.find({"city": id})
        response = json_util.dumps(houses)
        return Response(response, mimetype='application/json')
    return "hey"

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    if "username" in session:
        username = request.form["username"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        birthdate = request.form["birthdate"]
        
    return "you need to sign in to edit your profile"    



if __name__ == '__main__':
   app.run(debug=True)