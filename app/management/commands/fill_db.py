from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from faker import Faker
from django.db import IntegrityError
import random


class Command(BaseCommand):
    help = "Fill the database with test data"

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio of data population')

    def handle(self, *args, **options):
        fake = Faker()
        ratio = options['ratio']

        batch_size = 1000  # Разбиваем на батчи по 1000

        # Создание пользователей
        users = []
        for _ in range(ratio):
            while True:
                username = fake.user_name()
                if not User.objects.filter(username=username).exists():
                    user = User(username=username, email=fake.email())
                    users.append(user)
                    if len(users) >= batch_size:
                        User.objects.bulk_create(users, ignore_conflicts=True)
                        users.clear()
                    break

        if users:
            User.objects.bulk_create(users, ignore_conflicts=True)

        # Создание профилей
        profiles = []
        users = list(User.objects.all())  # Обновляем список пользователей
        for user in users:
            if not Profile.objects.filter(user=user).exists():
                profiles.append(Profile(user=user, avatar=None))
                if len(profiles) >= batch_size:
                    Profile.objects.bulk_create(profiles, ignore_conflicts=True)
                    profiles.clear()

        if profiles:
            Profile.objects.bulk_create(profiles, ignore_conflicts=True)

        # Создание тегов
        tags = []
        for _ in range(ratio):
            tag_name = fake.word()
            if not Tag.objects.filter(name=tag_name).exists():
                tags.append(Tag(name=tag_name))
                if len(tags) >= batch_size:
                    Tag.objects.bulk_create(tags, ignore_conflicts=True)
                    tags.clear()

        if tags:
            Tag.objects.bulk_create(tags, ignore_conflicts=True)

        # Создание вопросов
        questions = []
        tags = list(Tag.objects.all())  # Обновляем список тегов
        for _ in range(ratio * 10):
            author = random.choice(users) if users else None
            if author:
                question = Question(
                    title=fake.sentence(),
                    content=fake.text(),
                    author=author
                )
                questions.append(question)
                if len(questions) >= batch_size:
                    Question.objects.bulk_create(questions, ignore_conflicts=True)
                    questions.clear()

        if questions:
            Question.objects.bulk_create(questions, ignore_conflicts=True)

        # Добавление тегов к вопросам
        questions = list(Question.objects.all())  # Обновляем список вопросов
        for question in questions:
            if tags:
                question.tags.add(*random.sample(tags, random.randint(1, min(5, len(tags)))))

        # Создание ответов
        answers = []
        for _ in range(ratio * 100):
            author = random.choice(users) if users else None
            question = random.choice(questions) if questions else None
            if author and question:
                answer = Answer(
                    content=fake.text(),
                    author=author,
                    question=question,
                )
                answers.append(answer)
                if len(answers) >= batch_size:
                    Answer.objects.bulk_create(answers, ignore_conflicts=True)
                    answers.clear()

        if answers:
            Answer.objects.bulk_create(answers, ignore_conflicts=True)

        # Создание лайков для вопросов
        question_likes = []
        for _ in range(ratio * 200):
            user = random.choice(users) if users else None
            question = random.choice(questions) if questions else None
            if user and question and not QuestionLike.objects.filter(user=user, question=question).exists():
                question_like = QuestionLike(user=user, question=question)
                question_likes.append(question_like)
                if len(question_likes) >= batch_size:
                    QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)
                    question_likes.clear()

        if question_likes:
            QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Successfully populated the database with a ratio of {ratio}'))
