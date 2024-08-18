from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import Student, Mentor
from django.middleware.csrf import get_token
from ChatBot.models import  Question
import time 
class QuestionsListSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()  # or webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_student_can_access_questions_list(self):
        # Create test user
        student_user = get_user_model().objects.create_user(
            email="student@example.com",
            first_name="Student",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="123400789",
            gender="Male",
            password="Password123@",
        )

        # Create a few test questions
        for i in range(1, 6):
            Question.objects.create(
                user=student_user.id,  # Using the user's ID instead of a ForeignKey
                question_text=f"Sample Question {i}",
                level=i,
                original_question_id=i
            )

        # Open the login page
        print("Attempting to log in...")
        self.browser.get(self.live_server_url + "/users/login/")
        
        # Fill in the login form
        self.browser.find_element(By.NAME, "username").send_keys("student@example.com")
        self.browser.find_element(By.NAME, "password").send_keys("Password123@")

        # Submit the login form
        self.browser.find_element(By.CSS_SELECTOR, "button.login100-form-btn").click()

        # Check if login was successful by inspecting the current URL or page content
      

        # Now explicitly redirect to the questions list page
        print("Redirecting to the questions list...")
        self.browser.get(self.live_server_url + "/users/questions_list/")
        
        # Wait for the page to load and display the questions list
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.ID, "question-list"))
        )
        print("Questions list loaded.")

        # Verify the questions are displayed
        questions = self.browser.find_elements(By.CLASS_NAME, "question-item")
        self.assertTrue(len(questions) > 0)

        # Verify that the correct user level buttons are enabled
        user_level = 5  # Assuming the test student's level is 5
        for i in range(1, user_level + 1):
            button = self.browser.find_element(By.CSS_SELECTOR, f'button[data-level="{i}"]')
            self.assertFalse(button.get_attribute("disabled"))

        # Check that only questions of the active level are visible
        active_level = self.browser.find_element(By.CSS_SELECTOR, 'button.number-btn.active').get_attribute("data-level")
        visible_questions = [q for q in questions if q.is_displayed()]
        for question in visible_questions:
            self.assertEqual(question.get_attribute("data-level"), active_level)

        
        time.sleep(20)
