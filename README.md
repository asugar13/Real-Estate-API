Database schemas (enforced when writing to the DB):
var UserSchema = new Schema(
  {
    username:{
      type: String, required:true, len(username)<30
    },
    password: {
      type: String, required: true, len(password)<30
    },
    first_name: {
      type: String, len(first_name)<30
    },
    last_name: {
      type: String, len(last_name)<30
    }
    birthdate: {
      type: Date
    }
  }
)

primary key: username

var PropertySchema = new Schema(
  {
    name: {
      type: String, required: true, len(name)<30
    },
    city: {
      type: String, required: true
    },
    owner: {
      type: String, required: true
    },
    bedrooms: {
      type: Number, required: true
    },
    description: {
      type: String
    },
    additional_info: {
      type: String
    },
    type: {
      type: String
    }
  }
)

primary group key: owner, name, city


Routes:
/            
Methods: POST/GET
GET returns login.html      (learned how to render pages in Flask)
POST:
	Form data:
		username
		password
Logs you in and creates a session.


/signup
Methods: POST
Form data:
		username
		password
Signs you up in the users collection

/myhouses
Methods: GET, POST
GET:
	Returns a list of properties where you are the owner
POST:
	You can edit info about your own properties.
	Form data:
		City (required)
		Name (required)
		Description
		Bedrooms
		Type
		Additional_info
		New_name

/<id>/houses
Methods: GET, POST
GET:
	Returns all the properties in city id
POST: Posts a new property in city id
	Form data:
		Name (required)
		Bedrooms	(required)
		Description
		Type
		Additional_info

/profile
Methods: GET, POST
GET: Returns your user info
POST:
	You can edit the following user fields.
		Form data:
			First_name
			Last_name
			Birthdate

/logout
Method: GET
deletes your session.
