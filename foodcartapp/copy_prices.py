def copy_prices_to_orders(apps, schema_editor):
    OrderElement = apps.get_model('foodcartapp', 'OrderElement')
    order_elements = OrderElement.objects.all()
    for order_element in order_elements.iterator():
        order_element.price = order_element.product.price
        order_element.save()