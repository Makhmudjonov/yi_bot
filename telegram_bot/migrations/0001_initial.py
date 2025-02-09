# Generated by Django 5.1.5 on 2025-01-30 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('surname', models.CharField(max_length=255)),
                ('faculty', models.CharField(max_length=255)),
                ('course', models.IntegerField()),
                ('direction', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15, null=True)),
                ('material_type', models.CharField(max_length=50, null=True)),
                ('material_file_id', models.CharField(max_length=255, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
            ],
        ),
    ]
