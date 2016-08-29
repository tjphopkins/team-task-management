from collections import defaultdict
from todo.documents import Project, Team, Item


def user_dict(user):
    return {
        'name': user.name,
        'email': user.email,
        'avatar': user.avatar
    }


def team_dict(team):
    return {
        'name': team.name,
        'projects': [
            {'name': project.name, 'id': project.id}
            for project in Project.get_projects_for_team(team)
        ]}


def item_dict(item):
    assigned_to = getattr(item, 'assigned_to', None)
    if assigned_to:
        assigned_to = user_dict(assigned_to)
    completed_by = getattr(item, 'completed_by', None)
    if completed_by:
        completed_by = user_dict(completed_by)

    return {
        'text': item.text,
        'created_date': str(item.created_date),
        'assigned_to': assigned_to,
        'completed_date': getattr(item, 'completed_date', None),
        'completed_by': completed_by
    }


def todo_lists_dict(project):
    # Get all todo-list items for project to avoid doing a query for each list
    items = Item.get_all_for_project(project)
    todo_lists = defaultdict(list)
    for item in items:
        todo_lists[item.todo_list.id].append(item_dict(item))
    return todo_lists


def get_initial_data(user):
    """Get initial data for the user

    Returns an object of:
    user -- user logged into Todo
    teams -- teams that the user is a member of, including projects that
             the user is a contributor of
    """
    user = user_dict(user)
    teams = Team.get_teams_for_user(user)
    teams_list = []
    for team in teams:
        teams_list.append(team_dict(team))
    return {'user': user, 'teams': teams_list}
