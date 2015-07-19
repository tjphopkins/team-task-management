import unittest
from mock import patch
from mongoengine import ValidationError, OperationError
from datetime import datetime

from tests import TodoTestCase
from documents import User, Team


class TestTeam(TodoTestCase):

    def setUp(self):
        super(TestTeam, self).setUp()

        self.user, _ = User.create_or_update(
            '1234f5', 'Tom Hopkins', 'tomjphopkins@gmail.com',
            'http://image.com/image.jpg')
        self.user_2, _ = User.create_or_update(
            '5432g1', 'Christy O\'Reiley', 'coreiley@gmail.com',
            'http://image.com/image.jpg')

    def test_create_team(self):
        team, created = Team.create_or_update('Team Tom', [self.user])
        self.assertTrue(created)
        self.assertEqual(team.name, 'Team Tom')
        self.assertEqual(team.users, [self.user])

    def _create_team(self):
        self.team, _ = Team.create_or_update('Team Tom', [self.user])

    def test_deactivate_reactivate_and_update_name_and_users(self):
        self._create_team()
        self.team.deactivate()
        self.assertFalse(self.team.is_active)

        team, created = Team.create_or_update(
            'Team Tom', [self.user, self.user_2], new_name='Team Tim')

        self.assertFalse(created)
        self.team.reload()
        self.assertEqual(self.team, team)
        self.assertTrue(self.team.is_active)
        self.assertEqual(self.team.name, 'Team Tim')
        self.assertEqual(self.team.users, [self.user, self.user_2])

    def test_update_users_only(self):
        self._create_team()

        team, created = Team.create_or_update(
            'Team Tom', [self.user, self.user_2], new_name='Team Tim')

        self.assertFalse(created)
        self.team.reload()
        self.assertEqual(self.team.name, 'Team Tim')
        self.assertEqual(self.team.users, [self.user, self.user_2])

    def test_update_deactivated_do_not_reactivate(self):
        self._create_team()
        self.team.deactivate()
        self.assertFalse(self.team.is_active)

        with self.assertRaises(ValidationError):
            Team.create_or_update('Team Tom', [self.user, self.user_2],
                                  new_name='Team Tim', reactivate=False)

    def test_create_race(self):
        self._create_team()
        objects_patcher = patch(
            'todo.documents.Team.objects')
        mock_objects = objects_patcher.start()

        def raise_does_not_exist_once(*a, **k):
            objects_patcher.stop()
            raise Team.DoesNotExist

        mock_objects.get.side_effect = raise_does_not_exist_once

        Team.create_or_update('Team Tom', [self.user])

    @patch('todo.documents.Team.save')
    def test_create_other_operation_error(self, mock_save):
        def _raise_operation_error():
            raise OperationError('not duplicate key error')
        mock_save.side_effect = _raise_operation_error
        with self.assertRaises(OperationError):
            Team.create_or_update('Team Tom', [self.user])

    def test_user_teams(self):
        team1, _ = Team.create_or_update(
            'Team User', [self.user])
        team2, _ = Team.create_or_update(
            'Team User 2', [self.user])
        self.assertEqual([team1, team2], Team.user_teams(self.user))


class TestUser(TodoTestCase):

    def test_create_user(self):
        field = User.created_date
        mock_now = lambda: datetime(2015, 8, 1)
        with patch.object(field, 'default', new=mock_now):
            user, created = User.create_or_update(
                '1234f5', 'Tom Hopkins', 'tomjphopkins@gmail.com',
                'http://image.com/image.jpg')
        self.assertTrue(created)
        self.assertEqual(user.google_id, '1234f5')
        self.assertEqual(user.name, 'Tom Hopkins')
        self.assertEqual(user.email, 'tomjphopkins@gmail.com')
        self.assertEqual(user.avatar, 'http://image.com/image.jpg')
        self.assertEqual(user.created_date, datetime(2015, 8, 1))
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_anonymous)


if __name__ == '__main__':
    unittest.main()
