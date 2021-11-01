# Generated by Django 4.0a1 on 2021-10-31 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customuser_username'),
        ('history', '0004_game_moves'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='loser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loser', to='accounts.customuser'),
        ),
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='winner', to='accounts.customuser'),
        ),
    ]