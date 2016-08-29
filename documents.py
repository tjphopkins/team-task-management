from datetime import datetime
from mongoengine import OperationError, ValidationError
from todo import db


"""
Users are members of teams. Teams have projects. Users of a given team
may be contributors of one of the team's projects. Projects have TodoLists
and TodoLists have Items.

A Team knows which users belong to it.
A Project knows which team it belongs to.
A TodoList knows which project it belongs to and which items belong to it.
An Item is oblivious to the world.
"""


class User(db.Document):
    google_id = db.StringField(required=True)
    name = db.StringField(required=True)
    email = db.StringField(required=True)
    avatar = db.StringField()
    # Only authenticated and active users fulfill the criteria of
    # flask.ext.login.login_required view decorator
    is_authenticated = db.BooleanField(default=True)
    is_active = db.BooleanField(default=True)
    is_anonymous = db.BooleanField(default=False)
    created_date = db.DateTimeField(default=datetime.now())

    meta = {
        'indexes': [
            {
                'fields': ['email'],
                'unique': True
            },
            {
                'fields': ['google_id'],
                'unique': True
            },
        ]
    }

    @staticmethod
    def create_or_update(google_id, name, email, avatar, reactivate=True):
        """Create a new User or update with new properties. If the user is
        inactive and reactivate is True, user will be reactivated, otherwise an
        error will be raised.

        :return: Tuple containing user object and bool representing whether
        or not user was created
        """
        try:
            user = User.objects.get(google_id=google_id)
        except User.DoesNotExist:
            user = User(google_id=google_id, name=name, email=email,
                        avatar=avatar)
            user.save()
            return user, True
        else:
            if not user.is_active and not reactivate:
                raise ValidationError("User with this google_id is inactive")
            user.name = name
            user.email = email
            user.avatar = avatar
            user.is_active = True
            user.save()
        return user, False

    def get_id(self):
        return unicode(self.id)


class Item(db.Document):
    text = db.StringField(required=True)
    created_date = db.DateTimeField(default=datetime.now)
    assigned_to = db.EmbeddedDocumentField('User')
    completed_date = db.DateTimeField()
    completed_by = db.IntField()

    @staticmethod
    def get_all_for_project(project):
        return list(Item.objects.get(project=project))


class TodoList(db.Document):
    name = db.StringField(required=True)
    project = db.ReferenceField('Project', required=True)
    created_date = db.DateTimeField(
        default=datetime.now(), required=True
    )
    users = db.ListField(db.EmbeddedDocumentField('User'), required=True)
    items = db.ListField(db.EmbeddedDocumentField('Item'))

    meta = {
        'indexes': [
            {
                'fields': ['project', 'name'],
                'unique': True
            }
        ]
    }

    @staticmethod
    def create_or_update(name, project, users, new_name=None, reactivate=True):
        """Create a new TodoList, or update with new properties. If the
        list is inactive and reactivate is True, list will be reactivated,
        otherwise an error will be raised.
        """
        try:
            todo_list = TodoList.objects.get(name=name)
        except todo_list.DoesNotExist:
            todo_list = TodoList(name=name, users=users)
            try:
                todo_list.save()
            except OperationError as e:
                if 'E11000' in str(e):
                    return TodoList.create_or_update(
                        name, project, users, new_name=new_name,
                        reactivate=reactivate)
                else:
                    raise
            return todo_list, True
        else:
            if not todo_list.is_active and not reactivate:
                raise ValidationError("This todo_list is inactive")
            else:
                todo_list.is_active = True
                todo_list.name = new_name or name
                todo_list.project = project
                todo_list.users = users
                todo_list.save()
        return todo_list, False


class Project(db.Document):
    name = db.StringField(required=True)
    team = db.ReferenceField('Team', required=True)
    description = db.StringField(required=True)
    created_date = db.DateTimeField(
        default=datetime.now(), required=True
    )
    # A Project must have at least one user
    users = db.ListField(db.EmbeddedDocumentField('User'), required=True)

    meta = {
        'indexes': [
            {
                'fields': ['team', 'name'],
                'unique': True
            }
        ]
    }

    @staticmethod
    def create_or_update(name, team, description, users, to_do_lists,
                         new_name=None, reactivate=True):
        """Create a new Project, or update with new properties. If the project
        is inactive and reactivate is True, project will be reactivated,
        otherwise an error will be raised.
        """
        try:
            project = Project.objects.get(name=name)
        except Project.DoesNotExist:
            project = Project(name=name, users=users)
            try:
                project.save()
            except OperationError as e:
                if 'E11000' in str(e):
                    return Project.create_or_update(name, team, description,
                                                    users, to_do_lists)
                else:
                    raise
            return project, True
        else:
            if not project.is_active and not reactivate:
                raise ValidationError("This project is inactive")
            else:
                project.is_active = True
                project.name = new_name or name

                project.description = description
                project.users = users
                project.to_do_lists = to_do_lists
                project.save()
        return project, False

    @staticmethod
    def get_projects_for_team(team):
        return list(Project.objects.filter(team=team))


class Team(db.Document):
    name = db.StringField(required=True)
    created_date = db.DateTimeField(
        default=datetime.now(), required=True
    )
    # Must have at least one user
    users = db.ListField(db.EmbeddedDocumentField('User'), required=True)
    is_active = db.BooleanField(required=True, default=True)

    meta = {
        'indexes': [
            {
                'fields': ['name'],
                'unique': True
            },
            {
                'fields': ['users']
            }
        ]
    }

    @staticmethod
    def create_or_update(name, users, new_name=None, reactivate=True):
        """Create a new Team, or update with new users and/or new name. If the
        team is inactive, and reactivate is True, team will be reactivated,
        otherwise an error will be raised.
        """
        try:
            team = Team.objects.get(name=name)
        except Team.DoesNotExist:
            team = Team(name=name, users=users)
            try:
                team.save()
            except OperationError as e:
                if 'E11000' in str(e):
                    return Team.create_or_update(name, users)
                else:
                    raise
            return team, True
        else:
            if not team.is_active and not reactivate:
                raise ValidationError("This team is inactive.")
            else:
                team.is_active = True
                team.name = new_name or name
                team.users = users
                team.save()
        return team, False

    def deactivate(self):
        self.is_active = False
        self.save()

    @staticmethod
    def get_teams_for_user(user):
        return list(Team.objects.filter(users__in=[user]))
