# Generated by Django 5.1.4 on 2025-01-09 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_profile_avatar'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questiondislike',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='questiondislike',
            name='question',
        ),
        migrations.RemoveField(
            model_name='questiondislike',
            name='user',
        ),
        migrations.AddField(
            model_name='answerlike',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='questionlike',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='AnswerDislike',
        ),
        migrations.DeleteModel(
            name='QuestionDislike',
        ),
    ]
