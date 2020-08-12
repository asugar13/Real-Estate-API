# Instructions
1-Get the code on your local machine
```
$ git clone https://github.com/asugar13/Real-Estate-API.git
```
2- Create a clean new database directory inside the repo.
```
$ mkdir database
```
3- Run mongo on the new directory
```
$ mongod --dbpath database
```
4-Use python3 to run the server.py file
```
$ python3 server.py
```

Install any missing dependencies using pip. To install mongo please visit: https://docs.mongodb.com/manual/installation/



# Routes

/:
  - GET: Returns API instructions
  - POST: Required form data is:
       - "username"  (String less than 30 characters)
       - "password". (String, minimum 8 characters, at least one letter and one number)
       Logs you in and creates a session.

/signup:
  - POST: Required form data is:
      - "username" (30 characters max)
      - "password" (8 characters min, at least one letter and one number)
      Signs you up to the DB and returns a success/error message upon completion.

/profile:
  - GET: Returns user fields (except password) from session.
  - POST: Optional form data is:
      - "first_name" (15 characters max)
      - "last_name" (20 characters max, )
      - "birthdate" (in DD-MM-YYYY format)
      Updates the user fields to the DB with the given form data and returns the updated user object (except password field).

/myproperties:
  - GET: Returns JSON array with all the properties belonging to the user logged.
  - POST: Required form data is:
     - "city"  (one of ["paris", "lyon", "bruxelles", "marseille", "montreal"])
     - "name" (name of the logged in user's property to edit)
     - Optional form data is "description", "type" (one of ["loft", "condo", "apartment", "house", "mansion"]), "bedrooms" (valid integer) and "new_name" (if you want to change the property name).
     Updates the property fields to the DB with the given form data and returns the updated property object fields.

/<id>/properties:
  - GET: Returns a JSON array with all the properties in given city id (<id> should be one of: "paris", "lyon", "bruxelles", "marseille", "montreal".)
  - POST: Required form data is:
    - "name" (property name)  
    - "bedrooms" (valid integer).
    Optional form data is "description" (description of the property), "type" (one of "loft", "condo", "apartment", "house", "mansion") and "additional_info" (for any additional property information).

/logout:
- GET: Deletes user session and logs it out.
