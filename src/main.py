import unittest

from flask import (
    request,
    jsonify,
)
from flask_jwt_extended import jwt_required, get_jwt_identity

from src import create_app
from src.crud import get_todos, create_todo, delete_todo, update_todo
from src.database import get_db
from src.models import get_user_by_id, Todo

app = create_app()


@app.cli.command()
def test():
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner().run(tests)


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found.", "error": str(error)}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"message": "Internal server error, please try again later.", "error": str(error)}), 500


@app.route("/todos", methods=["GET"])
@jwt_required()
def get_all_todos():
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found."}), 404

    todos = get_todos(user_id=user.id)
    todos_json = [{"id": todo.id, "description": todo.description, "done": todo.done} for todo in todos]
    return jsonify(todos_json), 200

@app.route("/todos", methods=["POST"])
@jwt_required()
def add_todo():
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found."}), 404

    data = request.get_json()
    description = data.get('description')

    if not description:
        return jsonify({"message": "Description is required."}), 400

    new_todo = create_todo(user_id=user.id, description=description)
    return jsonify({
        "message": "Task created successfully!",
        "todo": {
            "id": new_todo.id,
            "description": new_todo.description,
            "done": new_todo.done
        }
    }), 201

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
@jwt_required()
def delete_task(todo_id):
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found."}), 404

    delete_todo(user_id=user.id, todo_id=todo_id)
    return jsonify({"message": "Task deleted successfully!"}), 200


@app.route("/todos/<int:todo_id>/toggle", methods=["PUT"])
@jwt_required()
def toggle_task_status(todo_id):
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found."}), 404

    db = next(get_db())
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.id).first()

    if todo:
        todo.done = not todo.done
        db.commit()
        return jsonify({
            "message": "Task status updated successfully!",
            "todo": {
                "id": todo.id,
                "description": todo.description,
                "done": todo.done
            }
        }), 200
    else:
        return jsonify({"message": "Task not found or you don't have permission to update it."}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)