from flask import Flask, request
from argon2 import PasswordHasher
from garble_functions import (
    username_exists,
    insert_user,
    generate_iv,
    get_iv,
    get_password_hash,
    generate_token,
    update_token,
    token_exists,
    get_note_id,
    get_author_from_token,
    insert_note,
    note_exists,
    get_note_authors,
    remove_note,
    update_note,
    get_all_notes,
    get_subnote_id,
    insert_subnote,
    update_subnote,
    subnote_exists,
    remove_subnote
)
import time

app = Flask(__name__)

ph = PasswordHasher()

@app.route("/register", methods=["POST"])
def post_register():
    data = request.get_json()

    username = data["username"]
    
    if username_exists(username):
        return "Username taken."
    
    password = data["password"]

    iv = generate_iv()
    password_hash = ph.hash(password + iv)


    user = {
        "username": username,
        "password_hash": password_hash,
        "iv": iv,
        "token": ""
    }

    insert_user(user)

    return "Account created."


@app.route("/authenticate", methods=["POST"])
def post_authenticate():
    data = request.get_json()

    username_attempt = data["username"]

    if not username_exists(username_attempt):
        return "Incorrect username or password."

    iv = get_iv(username_attempt)
    password_hash = get_password_hash(username_attempt)

    password_attempt = data["password"] + iv

    try:
        ph.verify(password_hash, password_attempt)

    except:
        return "Incorrect username or password."

    token = generate_token()

    update_token(username_attempt, token)

    return token


@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."

    id = get_note_id()
    title = data["title"]
    author = get_author_from_token(token)

    note = {
        "id": id,
        "title": title,
        "author": author,
        "modified": int(time.time())
    }

    insert_note(note)

    return "Note created."


@app.route("/notes", methods=["DELETE"])
def delete_note():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."

    note_id = data["note_id"]

    if not note_exists(note_id):
        return "Invalid note ID."
    
    authors = get_note_authors(note_id)
    author = get_author_from_token(token)

    if author not in authors:
        return "You are not allowed to modify this note."

    remove_note(note_id)

    return "Note deleted."


@app.route("/notes", methods=["PUT"])
def update_note_title():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."

    note_id = data["note_id"]

    if not note_exists(note_id):
        return "Invalid note ID."
    
    authors = get_note_authors(note_id)
    author = get_author_from_token(token)

    if author not in authors:
        return "You are not allowed to modify this note."
    
    title = data["title"]

    modified = int(time.time())

    update_note(note_id, title, modified)

    return "UPDATE /notes"


@app.route("/notes")
def get_notes():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."
    
    author = get_author_from_token(token)
    notes = get_all_notes(author)

    return notes


@app.route("/subnotes", methods=["POST"])
def post_subnote():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."

    note_id = data["note_id"]

    if not note_exists(note_id):
        return "Invalid note ID."

    subnote_id = get_subnote_id()
    content = data["content"]
    modified = int(time.time())

    subnote = {
        "id": subnote_id,
        "content": content,
        "modified": modified,
        "note_id": note_id
    }

    insert_subnote(subnote)

    return "POST /subnotes"


@app.route("/subnotes", methods=["PUT"])
def put_subnote():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."
    
    note_id = data["note_id"]

    if not note_exists(note_id):
        return "Invalid note ID."
    
    authors = get_note_authors(note_id)
    author = get_author_from_token(token)

    if author not in authors:
        return "You are not allowed to modify this subnote."
    
    subnote_id = data["subnote_id"]
    content = data["content"]
    modified = int(time.time())

    update_subnote(subnote_id, content, modified)

    return "Subnote updated."


@app.route("/subnotes", methods=["DELETE"])
def delete_subnote():
    data = request.get_json()

    token = data["token"]

    if not token_exists(token):
        return "Invalid token."
    
    note_id = data["note_id"]

    if not note_exists(note_id):
        return "Invalid note ID."

    author = get_author_from_token(token)
    authors = get_note_authors(note_id)

    if author not in authors:
        return "You are not allowed to modify this subnote."

    subnote_id = data["subnote_id"]

    if not subnote_exists(subnote_id):
        return "Invalid subnote ID."

    remove_subnote(subnote_id)

    return "Subnote deleted."


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
