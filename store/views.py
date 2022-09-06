from django.shortcuts import render
from . import models


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