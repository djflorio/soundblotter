from django.test import TestCase
from django.test import Client
from selenium import webdriver
import time
from django.core.urlresolvers import reverse
from accounts.models import Account
from django.contrib import auth
from django_webtest import WebTest
from django.conf import settings
import os, os.path

class BrowserAudioTestCase(WebTest):
    # Automatically called at beginning of each test
    def setUp(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('media.navigator.permission.disabled', True)
        profile.update_preferences()
        self.selenium = webdriver.Firefox(profile)
        
    # Automatically called at end of each test
    def tearDown(self):
        self.selenium.quit()
    
    # Test recording, deleting, and renaming
    def test_record_delete_rename(self):
        path = settings.MEDIA_ROOT + 'audio_uploads/4/'
        original_num = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        selenium = self.selenium
        selenium.get("http://localhost:8000/audio")
        email = selenium.find_element_by_id('post-email')
        password = selenium.find_element_by_id('post-pass')
        submit = selenium.find_element_by_id('login-button')
        # Login
        email.send_keys('tester@danflorio.com')
        password.send_keys('t3stus3r5ooo')
        submit.click()
        time.sleep(2)
        
        # Record for 2 seconds and make sure we have one more recording than before
        record = selenium.find_element_by_id('record_button')
        record.click()
        time.sleep(2)
        record.click()
        time.sleep(2)
        new_num = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        self.assertEqual(original_num + 1, new_num)
        
        # Rename the recording and make sure it worked
        rename = selenium.find_element_by_link_text('rename')
        rename.click()
        rename = selenium.find_element_by_id('audio_rename')
        submit = selenium.find_element_by_id('submit_rename')
        rename.clear()
        rename.send_keys('abcdefg')
        submit.click()
        title = selenium.find_element_by_class_name('audio-title-area')
        self.assertEqual(title.text[:7], "abcdefg")
        
        # Start renaming, but cancel, and make sure the name is the same
        rename = selenium.find_element_by_link_text('rename')
        rename.click()
        rename = selenium.find_element_by_id('audio_rename')
        rename.send_keys('blargh')
        cancel = selenium.find_element_by_class_name('cancel-button')
        cancel.click()
        title = selenium.find_element_by_class_name('audio-title-area')
        self.assertEqual(title.text[:7], "abcdefg")
        
        # Delete the recording and make sure we're back to original num of recordings
        delete = selenium.find_element_by_link_text('delete')
        delete.click()
        time.sleep(2)
        new_num = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        self.assertEqual(original_num, new_num)
        
        