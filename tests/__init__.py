import unittest

import todo
from todo.documents import User, Team, Project, Item, TodoList


class TodoTestCase(unittest.TestCase):

    def setUp(self):
        todo.app.config['MONGODB_SETTINGS'] = {'DB': "testing"}
        todo.app.config['TESTING'] = True
        todo.app.config['LOGIN_DISABLED'] = True

        self.app = todo.app.test_client()

        # Set the application context
        # (see http://kronosapiens.github.io/blog/2014/08/14
        # /understanding-contexts-in-flask.html)
        self.app_context = todo.app.app_context()
        self.app_context.push()
        # If we want to access the request object we can set the request
        # context on the fly like so:
        #   with app.test_request_context('/?name=Peter'):

    def tearDown(self):
        self.app_context.pop()

        User.drop_collection()
        Team.drop_collection()
        Project.drop_collection()
        Item.drop_collection()
        TodoList.drop_collection()
