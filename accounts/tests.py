from django.test import TestCase
from accounts.models import Account
from .forms import UserCreationForm, UserLoginForm
from django_webtest import WebTest
from django.contrib import auth
import hashlib
import random
from django.utils import timezone
import os.path
from django.conf import settings

class AccountTestCase(WebTest):
    testemail = "tester@test.com"
    testpassword = "good password 5000"
    
    def loginUser(self, email, password, active=True):
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            user = None
            
        if user is not None:
            if active:
                user.is_active = True
                user.save()
            page = self.app.get('/accounts/login/')
            page.form['username'] = email
            page.form['password'] = password
            page.form.submit()
        return user
    
    def setUp(self):
        email = self.testemail
        username = 'tester'

        # Generate activation key
        rnum = str(random.random()).encode('utf8')   
        salt = hashlib.sha1(rnum).hexdigest()[:5]
        usernamesalt = username + salt
        usernamesalt = usernamesalt.encode('utf8')
        
        activation_key = hashlib.sha1(usernamesalt).hexdigest()
        key_expires = timezone.now() + timezone.timedelta(days=2)
        
        user = Account.objects.create_user(email, username, self.testpassword)
        user.activation_key = activation_key
        user.key_expires = key_expires
        user.save()
    
    ################################################################
    # LOGIN TESTS                                                  #
    ################################################################
    
    def test_login_form_succeeds_with_correct_info_if_active(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 200)
    
    def test_login_form_fails_with_incorrect_password(self):
        self.loginUser(self.testemail, "wrongpassword")
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 302)
        
    def test_login_form_fails_with_nonexisting_email(self):
        self.loginUser("nonexisting@test.com", self.testpassword)
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 302)
    
    def test_login_form_fails_while_not_active(self):
        self.loginUser(self.testemail, self.testpassword, False)
        response = self.app.get('/accounts/dashboard')
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 302)
        
    def test_login_and_logout_works(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/dashboard/')
        self.assertContains(page, "tester")
        page = self.app.get('/accounts/logout/')
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 302)
        
    ################################################################
    # ACTIVATION TESTS                                             #
    ################################################################
        
    def test_activation_link_works(self):
        user = Account.objects.get(username="tester")
        activate_url = '/accounts/activate_user/' + user.activation_key
        page = self.app.get(activate_url)
        user = Account.objects.get(username="tester")
        self.assertEqual(user.is_active, True)
        
    def test_activation_displays_confirmation_page(self):
        user = Account.objects.get(username="tester")
        activate_url = '/accounts/activate_user/' + user.activation_key
        page = self.app.get(activate_url)
        self.assertContains(page, 'successful')
    
    def test_activation_link_fails_if_expired(self):
        user = Account.objects.get(username="tester")
        key_expires = timezone.now() - timezone.timedelta(days=2)
        user.key_expires = key_expires
        user.save()
        activate_url = '/accounts/activate_user/' + user.activation_key
        page = self.app.get(activate_url)
        user = Account.objects.get(username="tester")
        self.assertEqual(user.is_active, False)
        
    def test_activation_link_redirects_if_already_active(self):
        user = Account.objects.get(username="tester")
        user.is_active = True
        user.save()
        key_expires = timezone.now() - timezone.timedelta(days=2)
        user.key_expires = key_expires
        user.save()
        activate_url = '/accounts/activate_user/' + user.activation_key
        page = self.app.get(activate_url)
        self.assertContains(page, 'successful')
        
    def test_activation_link_redirects_if_none_user(self):
        page = self.app.get('/accounts/activate_user/badkey')
        self.assertContains(page, 'error')
        
    def test_new_activation_link_redirects_with_existing_user(self):
        user = Account.objects.get(username="tester")
        page = self.app.get('/accounts/new_activation_link/' + str(user.id))
        self.assertEqual(page.location, "/accounts/register_success")
        
    def test_new_activation_link_redirects_with_none_user(self):
        page = self.app.get('/accounts/new_activation_link/99')
        self.assertEqual(page.location, "/accounts/login")
        
    ################################################################
    # PASSWORD RESET TESTS                                         #
    ################################################################
        
    def test_pwreset_form_works(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page.form.submit()
        user = Account.objects.get(username="tester")
        self.assertEqual(user.pwreset, True)
        
    def test_pwreset_form_loads_confirm_template_if_valid_user(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page = page.form.submit()
        self.assertContains(page, 'tester@test.com')
        
    def test_pwreset_form_loads_fail_template_if_none_user(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = "tester2@test.com"
        page = page.form.submit()
        self.assertContains(page, 'email doesn\'t exist')
        
    def test_pwreset_view_works(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page.form.submit()
        user = Account.objects.get(username="tester")
        reset_link = '/accounts/r/' + str(user.id) + '/' + user.pwreset_key
        page = self.app.get(reset_link)
        page.form['new_password1'] = "brandnewpassword"
        page.form['new_password2'] = "brandnewpassword"
        page.form.submit()
        self.loginUser(self.testemail, "brandnewpassword")
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 200)
        
    def test_pwreset_view_shows_confirm_template(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page.form.submit()
        user = Account.objects.get(username="tester")
        reset_link = '/accounts/r/' + str(user.id) + '/' + user.pwreset_key
        page = self.app.get(reset_link)
        page.form['new_password1'] = "brandnewpassword"
        page.form['new_password2'] = "brandnewpassword"
        page = page.form.submit()
        self.assertContains(page, "successfully")
        
    def test_pwreset_view_shows_expired_template_if_key_expired(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page.form.submit()
        user = Account.objects.get(username="tester")
        user.pwreset_expires = timezone.now() - timezone.timedelta(days=2)
        user.save()
        reset_link = '/accounts/r/' + str(user.id) + '/' + user.pwreset_key
        page = self.app.get(reset_link)
        self.assertContains(page, "expired")
        
    def test_pwreset_view_shows_error_template_if_none_user(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page.form.submit()
        user = Account.objects.get(username="tester")
        reset_link = '/accounts/r/99/' + user.pwreset_key
        page = self.app.get(reset_link)
        self.assertContains(page, "error")
        
    def test_pwreset_view_shows_error_template_if_wrong_key(self):
        page = self.app.get('/accounts/forgot_pass/')
        page.form['email'] = self.testemail
        page.form.submit()
        user = Account.objects.get(username="tester")
        reset_link = '/accounts/r/' + str(user.id) + '/abcdefg1234567'
        page = self.app.get(reset_link)
        self.assertContains(page, "error")

    ################################################################
    # REGISTRATION TESTS                                           #
    ################################################################
    
    def test_register_form_succeeds_with_valid_info(self):
        page = self.app.get('/accounts/register/')
        page.form['email'] = "tester2@test.com"
        page.form['username'] = "tester2"
        page.form['password1'] = self.testpassword
        page.form['password2'] = self.testpassword
        page = page.form.submit()
        self.assertContains(page, 'confirmation')
        try:
            user = Account.objects.get(username="tester2")
        except Account.DoesNotExist:
            user = None
        self.assertNotEqual(user, None)
        
    def test_register_form_fails_with_taken_email(self):
        page = self.app.get('/accounts/register/')
        page.form['email'] = self.testemail
        page.form['username'] = "tester2"
        page.form['password1'] = self.testpassword
        page.form['password2'] = self.testpassword
        page = page.form.submit()
        self.assertContains(page, "address already exists")
        try:
            user = Account.objects.get(username="tester2")
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user, None)
        
    def test_register_form_fails_with_taken_username(self):
        page = self.app.get('/accounts/register/')
        page.form['email'] = "tester2@test.com"
        page.form['username'] = "tester"
        page.form['password1'] = self.testpassword
        page.form['password2'] = self.testpassword
        page = page.form.submit()
        self.assertContains(page, "username already exists")
        try:
            user = Account.objects.get(email="tester2@test.com")
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user, None)
        
    def test_register_form_fails_with_password_mismatch(self):
        page = self.app.get('/accounts/register/')
        page.form['email'] = "tester2@test.com"
        page.form['username'] = "tester2"
        page.form['password1'] = self.testpassword
        page.form['password2'] = "differentpassword"
        page = page.form.submit()
        self.assertContains(page, "do not match")
        try:
            user = Account.objects.get(email="tester2@test.com")
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user, None)
        
    ################################################################
    # SETTINGS TESTS                                               #
    ################################################################
        
    def test_settings_delete_works_with_no_user_directory(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/delete_user/')
        page.form['username'] = "tester"
        page.form.submit()
        try:
            user = Account.objects.get(username="tester")
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user, None)
    
    def test_settings_delete_works_with_user_directory(self):
        user = self.loginUser(self.testemail, self.testpassword)
        upload_directory = settings.MEDIA_ROOT + 'uploads/' + str(user.id) + '/'
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)
        f=open(upload_directory + "dummy.txt", "w+")
        f.write("Dummy file")
        f.close()
        page = self.app.get('/accounts/delete_user/')
        page.form['username'] = "tester"
        page.form.submit()
        try:
            user = Account.objects.get(username="tester")
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user, None)
        
    def test_settings_delete_fails_with_wrong_username(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/delete_user/')
        page.form['username'] = "tester2"
        page.form.submit()
        try:
            user = Account.objects.get(username="tester")
        except Account.DoesNotExist:
            user = None
        self.assertNotEqual(user, None)
        
    def test_settings_delete_shows_confirmation_page(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/delete_user/')
        page.form['username'] = "tester"
        page = page.form.submit()
        self.assertContains(page, "deleted")
        
    def test_settings_change_username_works(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/user_settings/')
        page.form['username'] = "testernew"
        page.form.submit()
        try:
            user = Account.objects.get(email=self.testemail)
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user.username, "testernew")
        
    def test_settings_change_email_works(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/user_settings/')
        page.form['email'] = "testernew@test.com"
        page.form.submit()
        try:
            user = Account.objects.get(username="tester")
        except Account.DoesNotExist:
            user = None
        self.assertEqual(user.email, "testernew@test.com")
        
    def test_change_password_works_with_correct_info(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/pass_settings/')
        page.form['new_password1'] = "password2"
        page.form['new_password2'] = "password2"
        page.form.submit()
        self.app.get('/accounts/logout/')
        page = self.app.get('/accounts/login/')
        page.form['username'] = self.testemail
        page.form['password'] = "password2"
        page.form.submit()
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 200)
        
    def test_change_password_shows_success_message(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/pass_settings/')
        page.form['new_password1'] = "password2"
        page.form['new_password2'] = "password2"
        page = page.form.submit()
        self.assertContains(page, "successfully")
        
    def test_change_password_fails_with_password_mismatch(self):
        self.loginUser(self.testemail, self.testpassword)
        page = self.app.get('/accounts/pass_settings/')
        page.form['new_password1'] = "password2"
        page.form['new_password2'] = "password3"
        page.form.submit()
        self.app.get('/accounts/logout/')
        page = self.app.get('/accounts/login/')
        page.form['username'] = self.testemail
        page.form['password'] = "password2"
        page.form.submit()
        page = self.app.get('/accounts/dashboard/')
        self.assertEqual(page.status_code, 302)