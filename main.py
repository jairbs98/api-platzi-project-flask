import unittest

from flask import (  # type: ignore
    request,
    make_response,
    redirect,
    render_template,
    session,
    flash,
    url_for,
)
from flask_login import login_required, current_user  # type: ignore

from app import create_app
from app.forms import TodoForm, DeleteTodoForm, UpdateTodoForm
from app.crud import get_todos, create_todo, delete_todo, update_todo
from app.database import get_db
from app.models import get_user

app = create_app()


@app.cli.command()
def test():
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner().run(tests)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html", error=error)


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html", error=error)


@app.route("/")
def index():
    user_ip = request.remote_addr
    response = make_response(redirect("/hello"))
    session["user_ip"] = user_ip
    return response


@app.route("/hello", methods=["GET", "POST"])
@login_required
def hello():
    db = next(get_db())  # Obtén una sesión de la base de datos
    user_ip = session.get("user_ip")
    user = get_user(current_user.id)  # Obtén el objeto User
    username = user.username  # Accede al username del usuario
    todo_form = TodoForm()
    delete_form = DeleteTodoForm()
    update_form = UpdateTodoForm()

    context = {
        "user_ip": user_ip,
        "todos": get_todos(user_id=user.id),  # Usa el ID numérico del usuario
        "username": username,
        "todo_form": todo_form,
        "delete_form": delete_form,
        "update_form": update_form,
    }

    if todo_form.validate_on_submit():
        create_todo(
            user_id=user.id,  # Usa el ID numérico del usuario
            description=todo_form.description.data,
        )

        flash("Your task was created successfully!")

        return redirect(url_for("hello"))

    return render_template("hello.html", **context)


@app.route("/todos/delete/<todo_id>", methods=["POST"])
def delete(todo_id):
    user = get_user(current_user.id)  # Obtén el objeto User
    user_id = user.id  # Usa el ID numérico del usuario
    delete_todo(user_id=user_id, todo_id=todo_id)

    return redirect(url_for("hello"))


@app.route("/todos/update/<todo_id>/<int:done>", methods=["POST"])
def update(todo_id, done):
    user = get_user(current_user.id)  # Obtén el objeto User
    user_id = user.id  # Usa el ID numérico del usuario
    update_todo(user_id=user_id, todo_id=todo_id, done=done)

    return redirect(url_for("hello"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
