from django.shortcuts import render
from . import models
from django.http.response import JsonResponse

import json
import datetime


def store(request):
    products = models.Product.objects.all()
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)

    else:
        order = {
            'get_cart_items': 0,
            'get_cart_total': 0
        }
    #cartItems = order.get_cart_items
    context = {
        'products': products,
        #'cartItems': cartItems,
        'order': order,
    }
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()

    else:
        order = {
            'get_cart_items': 0,
            'get_cart_total': 0
        }
    #cartItems = order.get_cart_items
    context = {
        'order': order,
        'orderitems': orderitems,
        #'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()

    else:
        order = {
            'get_cart_items': 0,
            'get_cart_total': 0
        }
    #cartItems = order.get_cart_items
    context = {
        'order': order,
        'orderitems': orderitems,
        #'cartItems': cartItems,
    }
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        product = models.Product.objects.get(id=productId)
        orderitem, created = models.OrderItem.objects.get_or_create(
            order=order,
            product=product,
        )

    if action == 'add':
        orderitem.quantity += 1
    elif action == 'remove':
        orderitem.quantity -= 1
    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()

    return JsonResponse(data, safe=False)


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer = models.Customer.objects.get(email=data['form']['email'])

    order = models.Order.objects.get(customer=customer, complete=False)

    total = int(data['form']['total'])
    transaction_id = datetime.datetime.now().timestamp()
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    models.ShippingInfo.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode']
    )
    return JsonResponse(data, safe=False)