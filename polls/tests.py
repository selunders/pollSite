import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):
	def test_was_published_recently_with_future_question(self):
		"""
		was_published_recently() returns False for questions whose pub_date
		is in the future.
		"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)
	
	def test_was_published_recently_with_old_question(self):
		"""
		was_published_recently() returns False for questions whose pub_date
		is older than 1 day.
		"""
		time = timezone.now() - datetime.timedelta(days=30)
		old_question = Question(pub_date=time)
		self.assertIs(old_question.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		"""
		was_published_recently() returns True for questions whose pub_date
		is less than 24 hrs ago
		"""
		time = timezone.now() - datetime.timedelta(hours=12)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
	"""
	Create Question with given 'question_text' and published
	the number of 'days' offset to now (negative for past, positive for future)
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text = question_text, pub_date = time)

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		"""
		If no questions exist, an appropriate message is displayed
		"""
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_past_question(self):
		"""
		Questions with a pub_date in the past are displayed
		on the index page
		"""
		question = create_question(question_text="Past Question", days=-30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			[question],
		)

	def test_future_question(self):
		"""
		Questions with a pub_date in the future are not
		displayed on the index page
		"""
		create_question(question_text="Future Question", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")

	def test_future_question_and_past_question(self):
		"""
		Even if both future and past questions exist, only
		past are displayed on the index page
		"""
		question = create_question(question_text="Past Question", days=-30)
		create_question(question_text="Future Question", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			[question]
		)

	def test_two_past_questions(self):
		"""
		The Questions index page may display multiple questions
		"""
		question1 = create_question(question_text="Past Question1", days=-30)
		question2 = create_question(question_text="Past Question2", days=-5)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			[question2, question1],
		)