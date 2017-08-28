from copy import copy
from itertools import chain

from django.test import TestCase
from rest_framework.test import APIClient


class ReviewAPITests(TestCase):
    """API Tests"""
    url = '/review/'
    sample = {
        'title': 'Test Title',
        'summary': 'Test Summary',
        'company': 'Test Company',
        'rating': 1,
    }
    auth_normal = {
        'username': 'user',
        'password': 'user1',
        'is_active': True,
    }
    auth_admin = {
        'username': 'admin',
        'password': 'admin1',
        'is_active': True,
        'is_staff': True,
    }

    def setUp(self):
        from django.contrib.auth.models import User
        for i in self.auth_admin, self.auth_normal:
            User.objects.create_user(**i)

    @staticmethod
    def login_as(creds):
        """Helper function to simplify login"""
        client = APIClient()
        return client if client.login(**creds) else None

    def test_login(self):
        """Check that logging-in works"""
        client = self.login_as(self.auth_normal)
        self.assertFalse(client is None)

    def test_auth_required_list(self):
        """Check that authentication is required to get a list of reviews"""
        client = APIClient()
        resp = client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_auth_required_post(self):
        """Check that authentication is required to POST a review"""
        client = APIClient()
        resp = client.post(self.url, self.sample)
        self.assertEqual(resp.status_code, 403)

    def test_required_fields(self):
        """Check that field requirements are enforced"""
        client = self.login_as(self.auth_normal)
        for i in self.sample:
            sample = copy(self.sample)
            del sample[i]
            resp = client.post(self.url, sample)
            self.assertEqual(resp.status_code, 400,
                             msg=('Field "%s" requirement not enforced' % i))

    def test_hidden_fields(self):
        """Check that the hidden fields are effectively being added"""
        client = self.login_as(self.auth_normal)
        resp = client.post(self.url, self.sample).json()
        for i in 'ipaddr', 'submission_date', 'reviewer':
            self.assertTrue(i in resp, msg=('Field "%s" not found' % i))

    def test_hidden_fields_ro(self):
        """Check that the hidden fields are read-only (i.e. ignored)"""
        client = self.login_as(self.auth_normal)
        test_data = (
            ('ipaddr', '90.244.39.13'),
            ('submission_date', '1991-08-25T20:57:08.000000'),
            ('reviewer', 'admin'),
        )
        for i, val in test_data:
            sample = copy(self.sample)
            sample[i] = val
            resp = client.post(self.url, sample).json()
            self.assertNotEqual(resp[i], val)

    def test_rating_range(self):
        """Check that it rejects out-of-range rating field"""
        client = self.login_as(self.auth_normal)
        for i in chain(range(-2, 1), range(6, 9)):
            sample = copy(self.sample)
            sample['rating'] = i
            resp = client.post(self.url, sample)
            self.assertEqual(resp.status_code, 400,
                             msg=('Field "%s" range not enforced' % i))

    def test_view_permissions(self):
        """Check that an user is blind to other users's reviews"""
        client1 = self.login_as(self.auth_admin)
        client2 = self.login_as(self.auth_normal)
        for i in range(0, 10):
            resp = (client1 if i % 2 else client2).post(self.url, self.sample)
            self.assertEqual(resp.status_code, 201)
        resp = client2.get(self.url)
        self.assertEqual(resp.status_code, 200)
        for i in resp.json():
            self.assertEqual(i['reviewer'], self.auth_normal['username'])
        resp = client2.get(self.url + '2/')
        self.assertEqual(resp.status_code, 404)
