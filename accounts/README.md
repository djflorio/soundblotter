# Django Accounts
### Custom accounts for end users.
#### Django v1.10
Includes registration with email authentication, login (with email address), dashboard, logout, user settings (change username/email/password), and a forgot password link. It uses JQuery for the login page.
### Getting Started
* Add all of the code into a directory named 'accounts' in your top-level project directory (as you would with any app).
* Add 'accounts' to to INSTALLED_APPS in settings.py.
* Change your settings to use Account as the auth user model:
 * AUTH_USER_MODEL = 'accounts.Account'
* Set the email backend to console output in settings.py. This makes it so emails are printed in the console rather than sent with a webserver (something you can configure later - this is good for development and for just getting started):
 * EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
* In order to send activation and password reset links to users, a SITE_BASE_URL must be set in the settings.py. For development, you can use localhost, and change it to your site's URL in production:
 * SITE_BASE_URL = "http://localhost:8000"
* Add a urlpattern for the app to urls.py like so:
 * url(r'^accounts/', include('accounts.urls')),
* Be sure to apply the migrations:
 * python manage.py migrate accounts
* Start your server, then navigate to '/accounts/login' to check it out!

### Email Configuration
* In settings.py, set the email address that users will recieve emails from:
 * DEFAULT_FROM_EMAIL = youremail@example.com
* The SMTP settings will depend on the mail server you use. Here are the settings that work with Zoho.com as an example:
 * EMAIL_HOST = "smtp.zoho.com"
 * EMAIL_PORT = 465
 * EMAIL_HOST_USER = (your Zoho username)
 * EMAIL_HOST_PASSWORD = (your Zoho password)
 * EMAIL_USE_SSL = True
* Remove the EMAIL_BACKEND setting, and Django will default to using SMTP. Now, assuming your SMTP settings are correct for your web server, the activation, activation resend, and password reset emails should all work as expected.

### Media Configuration (optional)
* If users will be uploading/saving to a media directory, first set the ENV_PATH in settings.py:
 * ENV_PATH = os.path.abspath(os.path.dirname(__file__))
* Use that to set the MEDIA_ROOT attribute:
 * MEDIA_ROOT = os.path.join(ENV_PATH, 'media/')
* Then set the MEDIA_URL:
 * MEDIA_URL = "/media/"
* Django Accounts assumes that uploads from users are kept in "media/uploads/[USER_ID]/"

### Testing
* If you want to use the tests written for this app, install django_webtest, then you can run:
 * python manage.py test accounts
 
### TODO
* Add success message when user settings are updated.
