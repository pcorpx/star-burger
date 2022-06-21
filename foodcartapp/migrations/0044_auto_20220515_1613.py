# Generated by Django 3.2 on 2022-05-15 11:13

from django.db import migrations


class Migration(migrations.Migration):

    def copy_prices_to_orders(apps, schema_editor):
        OrderElement = apps.get_model('foodcartapp', 'OrderElement')
        order_elements = OrderElement.objects.all()
        for order_element in order_elements.iterator():
            order_element.price = order_element.product.price
            order_element.save()

    dependencies = [
        ('foodcartapp', '0043_alter_orderelement_price'),
    ]

    operations = [
         migrations.RunPython(copy_prices_to_orders),
    ]
