from flask import Flask, request, Response, render_template
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId

import os;


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/realestatedb"
mongo = PyMongo(app)


@app.route("/", methods=['GET','POST'])
def index():
    if (request.method== "POST"):
        return "you posted me"

    else:
        return "you got me"
    
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        print(os.getcwd());
        return render_template("login.html")
    
@app.route("/houses", methods=["GET"])
def get_houses(): 
    houses = mongo.db.realestates.find()
    response = json_util.dumps(houses)
    return Response(response, mimetype='application/json')
    
    
@app.route('/<id>/houses', methods=["GET"])
def get_city_houses(id):
    houses = mongo.db.realestates.find({"city": id})
    response = json_util.dumps(houses)
    return response
    

if __name__ == '__main__':
   app.run(debug=True)