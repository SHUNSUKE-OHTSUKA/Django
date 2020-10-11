from django.test import TestCase

import datetime
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Create your tests here.


class QuestionModelTests(TestCase):
    def test_was_published_recently_whit_future_question(self):
        future_question = Question(pub_date=timezone.now() + datetime.timedelta(days=30))
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        old_question = Question(pub_date=timezone.now() - datetime.timedelta(days=1, seconds=1))
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recently_question(self):
        recently_question = Question(pub_date=timezone.now(
        ) - datetime.timedelta(hours=23, minutes=59, seconds=59))
        self.assertIs(recently_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTest(TestCase):
    # HTTP200、画面メッセージ：No polls are available.、質問リスト：空
    def test_no_question(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # 質問リスト：Past question.
    def test_past_question(self):
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 '<Question: Past question.>'])

    # 質問リスト：空(未来の質問は表示されない)
    def test_feature_question(self):
        create_question(question_text="Feature question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # 質問リスト：Past question.(未来の質問は表示されない)
    def test_feature_question_and_past_question(self):
        create_question(question_text="Feature question.", days=30)
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 '<Question: Past question.>'])

    # 質問リスト：Past question1.、Past question2.
    # 質問リストは最新投稿順に取得されるため、作成順序と取得順序が弱になることに注意
    def test_tow_past_question(self):
        create_question(question_text="Past question1.", days=-30)
        create_question(question_text="Past question2.", days=-10)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 '<Question: Past question2.>', '<Question: Past question1.>'])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
