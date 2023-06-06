# Generated by Django 4.2.2 on 2023-06-06 09:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('binary', models.FileField(upload_to='')),
                ('checksum', models.CharField(max_length=256, unique=True)),
                ('source', models.CharField(choices=[('YT', 'YouTube'), ('RAW', 'Raw File')], default='RAW', max_length=8)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NFT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_id', models.CharField(max_length=256, unique=True)),
                ('minting_tx', models.CharField(max_length=256)),
                ('uri', models.URLField()),
                ('content', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.content')),
            ],
        ),
    ]
