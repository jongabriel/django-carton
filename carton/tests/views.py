from django.http import HttpResponse

import json

from carton.cart import Cart
from carton.tests.models import Product

products = {}
products[1] = Product(name='deer', price=10.0, custom_id=1)
products[2] = Product(name='moose', price=20.0, custom_id=2)

def show(request):
    cart = Cart(request.session)
    response = ''
    for item in cart.items:
        response += '%(quantity)s %(item)s for $%(price)s\n' % {
            'quantity': item.quantity,
            'item': item.product.name,
            'price': item.subtotal,
        }
        response += 'items count: %s\n' % cart.count
        response += 'unique count: %s\n' % cart.unique_count
    return HttpResponse(response)


def add(request):
    cart = Cart(request.session)    
    product = products[int(request.POST.get('product_id'))]
    quantity = request.POST.get('quantity', 1)
    discount = request.POST.get('discount', 0)
    price = product.price - float(discount)
    cart.add(product, price, quantity)
    return HttpResponse()


def remove(request):
    cart = Cart(request.session)
    product = products[int(request.POST.get('product_id'))]
    cart.remove(product)
    return HttpResponse()


def remove_single(request):
    cart = Cart(request.session)
    initial_count = cart.count
    product = products[int(request.POST.get('product_id'))]
    cart.remove_single(product)
    after_rmv_count = cart.count
    assert initial_count == after_rmv_count + 1
    return HttpResponse()


def clear(request):
    cart = Cart(request.session)
    cart.clear()
    assert cart.count == 0
    return HttpResponse()


def set_quantity(request):
    cart = Cart(request.session)
    product = products[int(request.POST.get('product_id'))]
    quantity = request.POST.get('quantity')
    cart.set_quantity(product, quantity)    
    return HttpResponse()

def get_total(request):    
    cart = Cart(request.session)
    response_data = {}
    response_data['total_cost'] = str(cart.total)
    return HttpResponse(json.dumps(response_data), content_type="application/json")

'''
We're trusting the price sent to us. In a real-world 
scenario, the price would be changed internally from a trusted
source.
'''
def change_price(request):
    cart = Cart(request.session)
    product = products[int(request.POST.get('product_id'))]
    price = float(request.POST.get('price', product.price))
    quantity = request.POST.get('quantity', 1)
    cart.change_price(product, price, quantity)
    return HttpResponse()
    
def add_tax(request):
    cart = Cart(request.session)
    product = products[int(request.POST.get('product_id'))]
    tax = float(request.POST.get('tax', 0.0))
    cart.add_tax(product, tax)
    return HttpResponse()
    
        