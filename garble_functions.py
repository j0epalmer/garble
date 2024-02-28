from pymongo import MongoClient
from secrets import token_hex

client = MongoClient("localhost", 27017)
db = client["garble"]

users = db["users"]
notes = db["notes"]
subnotes = db["subnotes"]


def username_exists(username: str) -> None:
    data = {"username": username}
    query = users.find(data)
    query_result = list(query)

    if query_result:
        return True
    
    return False


def generate_iv() -> str:
    return token_hex()[:8]


def insert_user(user: dict) -> None:
    users.insert_one(user)


def get_iv(username: str) -> str:
    data = {"username": username}
    query = users.find(data)
    query_result = list(query)

    return query_result[0]["iv"]


def get_password_hash(username: str) -> str:
    data = {"username": username}
    query = users.find(data)
    query_result = list(query)

    return query_result[0]["password_hash"]


def token_exists(token: str) -> bool:
    data = {"token": token}
    query = users.find(data)
    query_result = list(query)

    if query_result:
        return True
    
    return False


def generate_token() -> str:
    token_valid = False

    while not token_valid:
        token = token_hex()

        if not token_exists(token):
            break

    return token


def update_token(username: str, token: str) -> None:
    user = {"username": username}
    updated_token = {"$set": {"token": token}}

    users.update_one(user, updated_token)


def get_note_id() -> int:
    num_notes = len(list(notes.find()))

    return num_notes + 1


def get_author_from_token(token: str) -> str:
    data = {"token": token}
    query = users.find(data)
    query_result = list(query)

    return query_result[0]["username"]


def insert_note(note: dict) -> None:
    notes.insert_one(note)


def note_exists(id: int) -> bool:
    data = {"id": id}
    query = notes.find(data)
    query_result = list(query)

    if query_result:
        return True
    
    return False


def get_note_authors(id: int) -> bool:
    data = {"id": id}
    query = notes.find(data)
    query_result = list(query)

    authors = query_result[0]["author"].split()

    return authors


def remove_note(id: int) -> None:
    note = {"id": id}
    
    notes.delete_one(note)


def update_note(note_id: int, title: str, modified: int) -> None:
    note = {"id": note_id}
    updated_title = {"$set": {"title": title, "modified": modified}}

    notes.update_one(note, updated_title)


def get_all_notes(author: str) -> list:
    found_notes = []
    all_notes = list(notes.find({}, {'_id': False}))

    for note in all_notes:
        if author in note["author"].split():
            found_notes.append(note)

    return found_notes


def get_subnote_id() -> int:
    num_notes = len(list(subnotes.find()))

    return num_notes + 1


def insert_subnote(subnote: dict) -> None:
    subnotes.insert_one(subnote)


def update_subnote(subnote_id: int, content: str, modified: int) -> None:
    subnote = {"id": subnote_id}
    updated_content = {"$set": {"content": content, "modified": modified}}

    subnotes.update_one(subnote, updated_content)


def subnote_exists(id: int) -> bool:
    data = {"id": id}
    query = subnotes.find(data)
    query_result = list(query)

    if query_result:
        return True
    
    return False


def remove_subnote(id: int) -> None:
    subnote = {"id": id}
    
    subnotes.delete_one(subnote)
