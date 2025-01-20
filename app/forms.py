from django import forms
from django.contrib.auth import authenticate

from .models import User, Profile, Question, Tag, Answer

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Enter your answer',
                'class': 'form-control',
                'rows': 5,
            }),
        }

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=255,
        help_text="Enter the tags separated by commas",
        widget=forms.TextInput(attrs={'placeholder': 'python, django'}),
    )

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'The subject of the question'}),
            'content': forms.Textarea(attrs={'placeholder': 'Question text'}),
        }

    def clean_tags(self):
        tags_input = self.cleaned_data['tags']
        tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]

        if len(tag_names) > 3:
            raise forms.ValidationError("You can add up to 3 tags only.")

        return tags_input

    def save(self, commit=True, **kwargs):
        author = kwargs.get('author')
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()

        tags_input = self.cleaned_data['tags']
        tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)

        return question

class ProfileEditForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

class AvatarEditForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['avatar']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Invalid username or password')
        self.user = user
        return data

    def get_authenticated_user(self):
        return self.user

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):
        data = super().clean()
        if data['password'] != data['password_confirmation']:
            self.add_error('password_confirmation', 'Passwords do not match')
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
