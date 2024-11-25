import os,sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('/workspaces/Sentimental-Analyzer-Pro/sentimental_analysis/')
print(sys.path)
import unittest
import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from settings import SECRET_KEY


class AuthenticationTests(unittest.TestCase):

    def test_register_page_status_code(self):
        """Test if the register page is accessible."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_status_code(self):
        """Test if the login page is accessible."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_template(self):
        """Test if the register page uses the correct template."""
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'authapp/register.html')

    def test_login_page_template(self):
        """Test if the login page uses the correct template."""
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'authapp/login.html')

    def test_register_success(self):
        """Test if user can successfully register."""
        response = self.client.post(reverse('register'), {
            'username': 'TestUser',
            'password1': 'ANicePassword123',
            'password2': 'ANicePassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='TestUser').exists())

    def test_register_wrong_password(self):
        """Test if user can't register with wrong password."""
        response = self.client.post(reverse('register'), {
            'username': 'TestUser',
            'password1': 'ANicePassword123',
            'password2': 'ANicePassword1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.")

    def test_register_short_password(self):
        """Test if registration fails with short password."""
        response = self.client.post(reverse('register'), {
            'username': 'TestUser',
            'password1': '123',
            'password2': '123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2',
                             "This password is too short. It must contain at least 8 characters.")

    def test_register_username_too_similar(self):
        """Test if registration fails with a password similar to username."""
        response = self.client.post(reverse('register'), {
            'username': 'TestUser',
            'password1': 'TestUser123',
            'password2': 'TestUser123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The password is too similar to the username.")

    def test_register_existing_username(self):
        """Test if registration fails with an existing username."""
        User.objects.create_user(username='existinguser', password='Password123')
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'password1': 'GoodPassword123',
            'password2': 'GoodPassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', "A user with that username already exists.")

    def test_register_empty_username(self):
        """Test if registration fails with an empty username."""
        response = self.client.post(reverse('register'), {
            'username': '',
            'password1': 'Password123',
            'password2': 'Password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', "This field is required.")

    def test_register_empty_password(self):
        """Test if registration fails with an empty password."""
        response = self.client.post(reverse('register'), {
            'username': 'TestUser',
            'password1': '',
            'password2': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password1', "This field is required.")

    def test_login_success(self):
        """Test if a user can log in with valid credentials."""
        User.objects.create_user(username='testuser', password='Password123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        """Test if login fails with an incorrect password."""
        User.objects.create_user(username='TestUser', password='Password123')
        response = self.client.post(reverse('login'), {
            'username': 'TestUser',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_login_wrong_username(self):
        """Test if login fails with an incorrect username."""
        User.objects.create_user(username='TestUser', password='Password123')
        response = self.client.post(reverse('login'), {
            'username': 'WrongUser',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_login_empty_username(self):
        """Test if login fails with an empty username."""
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_login_empty_password(self):
        """Test if login fails with an empty password."""
        response = self.client.post(reverse('login'), {
            'username': 'Testuser',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_logout(self):
        """Test if a logged-in user can log out."""
        user = User.objects.create_user(username='Testuser', password='Password123')
        self.client.login(username='Testuser', password='Password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_username_case_insensitive_login(self):
        """Test if login is case-sensitive for username."""
        User.objects.create_user(username='TestUser', password='Password123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_logout_redirect(self):
        """Test if a logged-out user is redirected to the login page."""
        user = User.objects.create_user(username='TestUser', password='Password123')
        self.client.login(username='TestUser', password='Password123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_homepage_not_access_for_no_authorization(self):
        """Test if the homepage is not accessible if not logged in."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main()