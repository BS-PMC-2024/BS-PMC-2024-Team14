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


from django.urls import reverse


class StudentFeedbackSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()  # or webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        # Create and save test student user
        self.student_user = get_user_model().objects.create_user(
            email="student@example.com",
            first_name="Student",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="123400789",
            gender="Male",
            password="Password123@",
        )
        self.student = Student.objects.create(
            id=self.student_user.id,
            email=self.student_user.email,
            first_name=self.student_user.first_name,
            last_name=self.student_user.last_name,
            phone=self.student_user.phone,
            birth_date=self.student_user.birth_date,
            passport_id=self.student_user.passport_id,
            gender=self.student_user.gender,
            level=5,
        )
        self.student_user.save()  # Save the user to ensure it's in the database

    def test_student_can_submit_feedback(self):
        # Open the login page
        print("Attempting to log in...")
        login_url = reverse('users:login')  # Use reverse to get the login URL
        self.browser.get(self.live_server_url + login_url)
        
        # Fill in the login form
        self.browser.find_element(By.NAME, "username").send_keys("student@example.com")
        self.browser.find_element(By.NAME, "password").send_keys("Password123@")

        # Submit the login form
        self.browser.find_element(By.CSS_SELECTOR, "button.login100-form-btn").click()

        # After successful login, redirect to student dashboard
        print("Redirecting to the student dashboard...")
        student_dashboard_url = reverse('users:student_dashboard')  # Use reverse to get the dashboard URL
        self.browser.get(self.live_server_url + student_dashboard_url)
        
        # Wait for the dashboard page to load
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "star-rating-mentor"))
        )
        print("Student dashboard loaded.")

        # Scroll down to the bottom of the page
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait briefly to ensure the page is fully scrolled

        # Ensure the star-rating-mentor input is clickable
        mentor_star_selector = "input#mentor_star5"
        star_element = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, mentor_star_selector))
        )

        # Attempt to click the star using JavaScript if direct clicking doesn't work
        self.browser.execute_script("arguments[0].click();", star_element)
        print("Clicked the mentor star element via JavaScript")

        # Submit the mentor rating form
        self.browser.find_element(By.CSS_SELECTOR, "form[action*='/student_feedback'] button.upload-button").click()

        # Wait for the redirect after submission
        WebDriverWait(self.browser, 10).until(
            EC.url_contains(self.live_server_url + student_dashboard_url)
        )

        print("Mentor rating submitted and verified.")

        # Optionally, verify that the stars are selected correctly after submission
        self.browser.get(self.live_server_url + student_dashboard_url)
        time.sleep(5)


