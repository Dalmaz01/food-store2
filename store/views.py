from django.shortcuts import render
from . import models
from django.http.response import JsonResponse

import json


def store(request):
    products = models.Product.objects.all()
    customer = request.user.customer
    order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    cartItems = order.get_cart_items
    context = {
        'products': products,
        'cartItems': cartItems,
    }
    return render(request, 'store/store.html', context)


def cart(request):
    customer = request.user.customer
    order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    orderitems = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {
        'order': order,
        'orderitems': orderitems,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    customer = request.user.customer
    order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    orderitems = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {
        'order': order,
        'orderitems': orderitems,
        'cartItems': cartItems,
    }
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

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
