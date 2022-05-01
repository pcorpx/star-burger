import json
from django.http import JsonResponse
from django.templatetags.static import static


from .models import Product, Order, OrderElement


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    try:
        requested_order = json.loads(request.body.decode())
        print(requested_order)
        created_order = Order.objects.create(
            firstname=requested_order['firstname'],
            lastname=requested_order['lastname'],
            phone_number=requested_order['phonenumber'],
            address=requested_order['address'],
        )
        for requested_product in requested_order['products']:
            product_id = requested_product['product']
            quantity = requested_product['quantity']
            product = Product.objects.get(id=product_id)
            OrderElement.objects.create(
                order=created_order,
                product=product,
                quantity=quantity,
            )
        return JsonResponse({}, status=200)
    except ValueError:
        return JsonResponse(
            {'error': 'Invalid value was provided'},
            status=400
        )
