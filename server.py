from flask import Flask, request
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/realstatedb"
mongo = PyMongo(app)

@app.route("/", methods=['GET','POST'])
def index():
    if (request.method== "POST"):
        return "you posted me"

    else:
        return "you got me"
    
@app.route("/house", methods=["POST"])
def create_house():
    
    

#if __name__ == '__main__':
 #   app.run(debug=True)