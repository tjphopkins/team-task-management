import unittest

from tests import TodoTestCase
from documents import User, Team


class TestViews(TodoTestCase):

    def setUp(self):
        super(TestViews, self).setUp()

        self.user, _ = User.create_or_update(
            '1234f5', 'Tom Hopkins', 'tomjphopkins@gmail.com',
            'http://image.com/image.jpg')
        team1, _ = Team.create_or_update(
            'Team 1', [self.user])
        team2, _ = Team.create_or_update(
            'Team 2', [self.user])


if __name__ == '__main__':
    unittest.main()
