
from flask import Blueprint, Flask, jsonify, request, g
from dotenv import load_dotenv
import os
import jwt
import bcrypt
import psycopg2, psycopg2.extras
from db_helpers import get_db_connection
from auth_middleware import token_required

authentication_blueprint = Blueprint('authentication_blueprint', __name__)

@authentication_blueprint.route('/')
def index():
  return "Hello, world!"

@authentication_blueprint.route('/sign-token', methods=['GET'])
def sign_token():
  user = {
    "id": 1,
    "username": "test",
    "password": "test"
  }
  token = jwt.encode(user, os.getenv('JWT_SECRET'), algorithm="HS256")

  return jsonify({"token": token})

@authentication_blueprint.route('/verify-token', methods=['POST'])
def verify_token():
  try:
    token = request.headers.get('Authorization').split(' ')[1]
    decoded_token = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms="HS256")
    return jsonify({ "user": decoded_token })
  except Exception as error:
    return jsonify({"error": error.message})
  
@authentication_blueprint.route('/auth/signup', methods=['POST'])
def signup():
    try:
        new_user_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s;", (new_user_data["username"],))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            return jsonify({"error": "Username already taken"}), 400
        hashed_password = bcrypt.hashpw(bytes(new_user_data["password"], 'utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING username", (new_user_data["username"], hashed_password.decode('utf-8')))
        created_user = cursor.fetchone()
        connection.commit()
        connection.close()

        token = jwt.encode(created_user, os.getenv('JWT_SECRET'))
        return jsonify({"token": token, "user": created_user}), 201
    
    except Exception as error:
        print(error)
        return jsonify({"error": str(error)}), 401


@authentication_blueprint.route('/auth/signin', methods=["POST"])
def signin():
    try:
        sign_in_form_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s;", (sign_in_form_data["username"],))
        existing_user = cursor.fetchone()
        if existing_user is None:
            return jsonify({"error": "Invalid credentials."}), 401
        password_is_valid = bcrypt.checkpw(bytes(sign_in_form_data["password"], 'utf-8'), bytes(existing_user["password"], 'utf-8'))
        if not password_is_valid:
            return jsonify({"error": "Invalid credentials."}), 401
        
        
        # Updated code:
        token = jwt.encode({"username": existing_user["username"], "id": existing_user["id"]}, os.getenv('JWT_SECRET'))
        return jsonify({"token": token}), 201
    
    except Exception as error:
        return jsonify({"error": "Invalid credentials."}), 401
    finally:
        connection.close()

@authentication_blueprint.route('/vip-lounge')
@token_required
def vip_lounge():
  return f"Welcome to the party, {g.user['username']}"