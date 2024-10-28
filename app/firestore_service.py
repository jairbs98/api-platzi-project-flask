import os
from google.cloud import firestore

if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    raise ValueError(
        "La variable de entorno GOOGLE_APPLICATION_CREDENTIALS no está configurada."
    )

db = firestore.Client()


def get_users():
    return db.collection("users").get()


def get_user(user_id):
    return db.collection("users").document(user_id).get()


def user_put(user_data):
    user_ref = db.collection("users").document(user_data.username)
    user_ref.set({"password": user_data.password})


def get_todos(user_id):
    return db.collection("users").document(user_id).collection("todos").get()


def put_todo(user_id, description):
    todos_collection_ref = db.collection("users").document(user_id).collection("todos")
    todos_collection_ref.add({"description": description, "done": False})


def delete_todo(user_id, todo_id):
    todo_ref = _get_todo_ref(user_id, todo_id)
    todo_ref.delete()


def update_todo(user_id, todo_id, done):
    todo_done = not bool(done)
    todo_ref = _get_todo_ref(user_id, todo_id)
    todo_ref.update({"done": todo_done})


def _get_todo_ref(user_id, todo_id):
    return db.document("users/{}/todos/{}".format(user_id, todo_id))
