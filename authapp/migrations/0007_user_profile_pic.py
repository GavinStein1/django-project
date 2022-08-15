# Generated by Django 3.2.5 on 2022-08-15 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0006_remove_user_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_pic',
            field=models.FilePathField(default='/media/profiles/default.jpg', path='/media/profiles/default.jpg'),
            preserve_default=False,
        ),
    ]