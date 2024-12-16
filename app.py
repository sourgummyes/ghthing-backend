# app.py
#FULL BAND IS 5 LETTER YES NO
#IN THIS ORDER
#VOCALS  GUITAR  BASS  KEYS  DRUMS
from auth_middleware import token_required

from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
import os
import jwt
import bcrypt
import psycopg2, psycopg2.extras

from auth_blueprint import authentication_blueprint
from songs_blueprint import songs_blueprint

load_dotenv()

# Initialize Flask
# We'll use the pre-defined global '__name__' variable to tell Flask where it is.
app = Flask(__name__)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(songs_blueprint)

# Define our route
# This syntax is using a Python decorator, which is essentially a succinct way to wrap a function in another function.


# Run our application, by default on port 5000
if __name__ == '__main__':
    app.run()
