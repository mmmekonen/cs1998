import json
from flask import Flask, request
import db


DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(body, code=200):
    return json.dumps(body), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


@app.route("/tasks/")
def get_tasks():
    return success_response({"tasks": DB.get_all_tasks()})


@app.route("/tasks/", methods=["POST"])
def create_task():
    body = json.loads(request.data)
    description = body["description"]
    task_id = DB.insert_task_table(description, False)
    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Something went wrong while creating task!", 500)
    return success_response(task, 201)


@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Task not found!")
    return success_response(task)


@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    body = json.loads(request.data)
    description = body["description"]
    done = bool(body["done"])
    DB.update_task_by_id(task_id, description, done)

    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Task not found!")
    return success_response(task)


@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Task not found!")
    DB.delete_task_by_id(task_id)
    return success_response(task)


@app.route("/task/<int:task_id>/subtasks/", methods=[POST])
def create_subtask(task_id):
    body = json.loads(request.data)
    description = body["description"]

    try:
        subtask = {
            "id": DB.insert_subtask(description, False, task_id),
            "description": description,
            "done": False,
            "task_id": task_id,
        }
        return json.dumps({"success": True, "data": subtask})
    except sqlite3.IntegrityError:
        return json.dumps({"success": False, "error": "Task not found!"}), 404


@app.route("/task/<int:task_id>/subtasks/")
def get_subtasks_of_task(task_id):
    res = {"subtasks": DB.get_subtasks_of_task(task_id)}
    return json.dumps(res), 200
