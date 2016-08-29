import json

from flask import render_template
from flask.ext.login import login_required, current_user

from todo import app
from todo.documents import Project
import todo.api as api


@app.route('/')
def index():
    """Renders the app template which initialises the ReactJS application with
    the initial data.
    """
    initial_data = api.get_initial_data(current_user)
    return render_template('index.html', initial_data)


@app.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    """Returns project data."""
    project = Project.objects.get(id=project_id)
    return json.dumps(api.todo_lists_dict(project))
