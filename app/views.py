from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect
from .forms import LoginForm, UserForm, ProfileEditForm, AvatarEditForm, QuestionForm, AnswerForm
from .models import Question, Tag, Profile
from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth import login as auth_login

def paginate(object_list, request, per_page=10):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(object_list, per_page)
    page = paginator.page(page_num)
    return page

def index(request):
    questions = Question.objects.get_new_questions()
    page = paginate(questions, request, 5)
    return render(request, template_name='index.html', context={
        'questions': page.object_list, 'page_obj': page
    })

def hot(request):
    hot_questions = Question.objects.get_best_questions()
    page = paginate(hot_questions, request, 5)
    return render(request, template_name='hot_questions.html', context={
        'questions': page.object_list, 'page_obj': page
    })

@login_required
def ask(request):
    form = QuestionForm()
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save(author=request.user)
            return redirect(reverse('one_question', kwargs={'question_id': form.instance.id}))
    return render(request, template_name='ask.html', context={
        'form': form
    })

@login_required
def one_question(request, question_id):
    one_question = Question.objects.get(id=question_id)
    answers = one_question.answers.all()
    form = AnswerForm()
    page = paginate(answers, request, 5)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = one_question  # Привязываем к вопросу
            answer.save()
            return redirect('one_question', question_id=one_question.id)

    return render(request, template_name='one_question.html', context={
        'item': one_question,
        'answers': page.object_list, 'page_obj': page,
        'form': form
    })

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.get_authenticated_user())
            return redirect(reverse('index'))
    return render(request, template_name='login.html', context={
        'form': form
    })

def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))

def signup(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            user = auth.authenticate(request, **form.cleaned_data)
            auth.login(request, user)
            Profile.objects.create(user=user)
            return redirect(reverse('index'))
    return render(request, template_name='signup.html', context={
        'form': form
    })

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.filter(tags=tag).order_by('-created_at')
    page = paginate(questions, request, 5)
    return render(request, template_name='tag.html', context={
        'questions': page.object_list, 'page_obj': page,
        'tag': tag
    })

@login_required
def settings(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    user = request.user.profile
    profile_form = ProfileEditForm()
    avatar_form = AvatarEditForm()
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=request.user)
        avatar_form = AvatarEditForm(request.POST, request.FILES, instance=user)
        if profile_form.is_valid() and avatar_form.is_valid():
            profile_form.save()
            avatar_form.save()
            return redirect(reverse('settings'))
    return render(request, 'settings.html', context={
        'profile_form': profile_form,
        'avatar_form': avatar_form
    })

