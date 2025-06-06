# Generated by Django 5.1.5 on 2025-04-04 17:48

import Discussion.models
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Coordinator', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='Discussion.question')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='Discussion.quiz'),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.TextField(blank=True, null=True)),
                ('document', models.FileField(blank=True, null=True, upload_to=Discussion.models.session_document_path)),
                ('host', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='hosted_main_sessions', to=settings.AUTH_USER_MODEL)),
                ('quiz', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_quiz', to='Discussion.quiz')),
                ('users_accessed_react', models.ManyToManyField(blank=True, related_name='sessions_accessed_react', to=settings.AUTH_USER_MODEL)),
                ('users_joined', models.ManyToManyField(related_name='joined_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='quiz',
            name='session',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quiz_session', to='Discussion.session'),
        ),
        migrations.CreateModel(
            name='UserRoleInSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('is_current', models.BooleanField(default=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coordinator.role')),
                ('session', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Discussion.session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuizRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('score', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quiz', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='quiz_records', to='Discussion.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('quiz', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['date'], name='Discussion__date_49b7c1_idx'),
        ),
    ]
