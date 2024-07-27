from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Account
from decimal import Decimal
from django.core.management import call_command


class UserAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('migrate')

    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(username='staffuser', password='staffpass', is_staff=True)
        self.normal_user = User.objects.create_user(username='normaluser', password='userpass')
        self.verified_user = User.objects.create_user(username='verifieduser', password='userpass')
        Account.objects.create(user=self.staff_user, is_verified=False, balance=Decimal('0.00'))
        Account.objects.create(user=self.normal_user, is_verified=False, balance=Decimal('0.00'))
        Account.objects.create(user=self.verified_user, is_verified=True, balance=Decimal('100.00'))


    def test_user_registration(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass',
            'first_name': 'Test',
            'last_name': 'User',
            'city': 'Test City',
            'country': 'Test Country'
        }
        response = self.client.post('/user/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Account.objects.filter(user__username='testuser').exists())

    def test_user_list_staff_only(self):
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='normaluser', password='userpass')
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_filter(self):
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get('/user/?username=verified')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'verifieduser')

    def test_user_update_staff_only(self):
        self.client.login(username='staffuser', password='staffpass')
        data = {'first_name': 'Updated'}
        response = self.client.patch(f'/user/{self.normal_user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Updated')

        self.client.login(username='normaluser', password='userpass')
        response = self.client.patch(f'/user/{self.normal_user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_staff_only(self):
        self.client.logout()
        self.client.login(username='normal', password='pass')
        response = self.client.delete(f'/user/{self.normal_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.delete(f'/user/{self.normal_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_verify_user_staff_only(self):
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.post(f'/user/{self.normal_user.id}/verify/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.account.refresh_from_db()
        self.assertTrue(self.normal_user.account.is_verified)

        self.client.login(username='normaluser', password='userpass')
        response = self.client.post(f'/user/{self.staff_user.id}/verify/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_balance_staff_only(self):
        self.client.login(username='staffuser', password='staffpass')
        data = {'amount': 50.00}
        response = self.client.post(f'/user/{self.verified_user.id}/change_balance/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verified_user.account.refresh_from_db()
        self.assertEqual(self.verified_user.account.balance, Decimal('150.00'))

        self.client.login(username='normaluser', password='userpass')
        response = self.client.post(f'/user/{self.verified_user.id}/change_balance/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_balance_verified_only(self):
        self.client.login(username='staffuser', password='staffpass')
        data = {'amount': 50.00}
        response = self.client.post(f'/user/{self.normal_user.id}/change_balance/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)