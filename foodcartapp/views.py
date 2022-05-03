import json
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


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


@api_view(['POST'])
def register_order(request):
    err_content = 'Invalid data was provided'
    try:
        req_order = json.loads(request.body.decode())
        print(req_order)
        order_elem = {'product', 'quantity'}
        if 'products' not in req_order:
            err_content = 'There is no products list in order'
            raise ValueError
        if not isinstance(req_order['products'], list):
            err_content = 'The products value should be a list'
            raise ValueError
        if not req_order['products']:
            err_content = 'The products list can\'t be an empty'
            raise ValueError
        if any([not isinstance(req_product, dict)
                or not order_elem.issubset(set(req_product.keys()))
                for req_product in req_order['products']]):
            err_content = 'Invalid products items in the list was provided'
            raise ValueError
        created_order = Order.objects.create(
            firstname=req_order['firstname'],
            lastname=req_order['lastname'],
            phone_number=req_order['phonenumber'],
            address=req_order['address'],
        )
        for req_product in req_order['products']:
            if isinstance(req_product['product'], str) and \
               not req_product['product'].isdigit():
                err_content = 'The product id should be a digit'
                raise
            if isinstance(req_product['product'], (str, int)) and \
               Product.objects.filter(id=req_product['product']) \
                              .exists():
                product_id = req_product['product']
                product = Product.objects.get(id=product_id)
            else:
                err_content = 'Non existent product was provided'
                raise ValueError
            if isinstance(req_product['quantity'], str) and \
               not req_product['quantity'].isdigit():
                err_content = 'The quantity should be a digit'
                raise
            if isinstance(req_product['product'], (str, int)) and \
               int(req_product['quantity']) in range(1, 999):
                quantity = req_product['quantity']
            else:
                err_content = 'Quantity of product should be between ' \
                    '1 and 999'
                raise ValueError
            OrderElement.objects.create(
                order=created_order,
                product=product,
                quantity=quantity,
            )
        return Response({}, status=200)
    except ValueError:
        return Response(
            {'error': err_content},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )
