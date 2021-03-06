# Generated by Django 2.1.7 on 2020-05-30 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appuser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='building',
            field=models.CharField(blank=True, default='', max_length=64, null=True, verbose_name='Номер строения'),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Страна'),
        ),
        migrations.AlterField(
            model_name='address',
            name='district',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Район'),
        ),
        migrations.AlterField(
            model_name='address',
            name='flat',
            field=models.CharField(blank=True, default='', max_length=64, null=True, verbose_name='Номер квартиры'),
        ),
        migrations.AlterField(
            model_name='address',
            name='house',
            field=models.CharField(blank=True, default='', max_length=64, null=True, verbose_name='Номер дома'),
        ),
        migrations.AlterField(
            model_name='address',
            name='postcode',
            field=models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='Почтовый индекс'),
        ),
        migrations.AlterField(
            model_name='address',
            name='region',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Область'),
        ),
        migrations.AlterField(
            model_name='address',
            name='settlement',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Населенный пункт'),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Улица'),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='email',
            field=models.EmailField(default='f5e7840561b348c894054b8f7b9d74b4', max_length=255, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='phone',
            field=models.CharField(default='47a3e36e96c343fab27f5eae85c3fd67', max_length=255, unique=True, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='username',
            field=models.CharField(default='eb42cc17e9944677bf895601a4995cb4', error_messages={'unique': 'Пользователь с таким логином уже существует!'}, max_length=150, unique=True, verbose_name='Логин'),
        ),
    ]
