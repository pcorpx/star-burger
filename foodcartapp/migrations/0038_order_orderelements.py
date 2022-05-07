# Generated by Django 3.2 on 2022-05-01 08:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=50, verbose_name='Имя')),
                ('lastname', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='Номер телефона')),
            ],
        ),
        migrations.CreateModel(
            name='OrderElements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(999)], verbose_name='количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_elements', to='foodcartapp.order', verbose_name='заказ')),
                ('product', models.ForeignKey(default='снят с продажи', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='order_elements', to='foodcartapp.product', verbose_name='продукт')),
            ],
        ),
    ]