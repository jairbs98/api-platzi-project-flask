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
    # Guarda el documento y obtén su referencia
    doc_ref = todos_collection_ref.add({"description": description, 'done': False})
    # Regresa el ID del documento recién creado
    return doc_ref[1].id


def delete_todo(user_id, todo_id):
    # Accede al documento "todo" usando el ID
    todo_ref = db.collection('users').document(user_id).collection('todos').document(todo_id)
    todo_ref.delete()


def update_todo(user_id, todo_id, done):
    todo_done = not bool(done)
    # Accede al documento "todo" usando el ID
    todo_ref = db.collection('users').document(user_id).collection('todos').document(todo_id)
    todo_ref.update({'done': todo_done})