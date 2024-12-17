from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

songs_blueprint = Blueprint('songs_blueprint', __name__)

@songs_blueprint.route('/songs', methods=['GET'])
def songs_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT id, author, title, album, fullband
            FROM songs;
        """)
        songs = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"songs": songs}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    

@songs_blueprint.route('/songs', methods=['POST'])
@token_required
def create_song():
    try:
        new_song = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO songs (author, title, album, fullband)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_song['author'], new_song['title'], new_song['album'], new_song['fullband'])
        )
        created_song = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"song": created_song}), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@songs_blueprint.route('/songs/<song_id>', methods=['PUT'])
@token_required
def update_song(song_id):

    try:
        updated_song_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM songs WHERE songs.id = %s", (song_id,))
        song_to_update = cursor.fetchone()
        if song_to_update is None:
            return jsonify({"error": "song not found"}), 404
        connection.commit()
        cursor.execute("""
            UPDATE songs 
            SET title = %s, album = %s, fullband = %s 
            WHERE songs.id = %s 
            RETURNING *;
        """, 
            (updated_song_data["title"], updated_song_data["album"], updated_song_data["fullband"], song_id))
        updated_song = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"song": updated_song}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

    
@songs_blueprint.route('/songs/<song_id>', methods=['GET'])
def show_song(song_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT id, author, title, album, fullband
            FROM songs
            WHERE id = %s;
        """, (song_id,))
        song = cursor.fetchall()
        if song:
            connection.close()
            return jsonify({"song": song[0]}), 200
        else:
            connection.close()
            return jsonify({"error": "Song not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@songs_blueprint.route('/songs/<song_id>', methods=['DELETE'])
@token_required
def delete_song(song_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM songs WHERE songs.id = %s", (song_id,))
        song_to_delete = cursor.fetchone()
        if song_to_delete is None:
            return jsonify({"error": "Song not found"}), 404
        connection.commit()
        cursor.execute("DELETE FROM songs WHERE songs.id = %s", (song_id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Song deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
