from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse

from . import models
from django.http.response import JsonResponse
from django.contrib.auth.models import User

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
        orderitems = []
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
        orderitems = []
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


def register_page(request):
    '''
    Контроллер, отвечающий за логику:
    - отображения страницы регистрации
    - регистрации пользователя
    '''
    if request.method == "POST":
        # Регистрация пользователя при POST запросе
        try:
            username = request.POST.get("login", None)
            password = request.POST.get("password", None)
            email = request.POST.get("email", None)
            name = request.POST.get("name", None)

            user = User.objects.create_user(
                username=username,
                password=password
            )

            models.Customer.objects.create(
                user=user,
                name=name,
                email=email
            )
            return redirect(reverse('store:login'))
        except Exception as exc:
            print("При создании пользователя произошла ошибка", request.POST, exc)
            error = {
                'error_code': exc,
                'message': 'Проверьте корректность введенных данных'
            }
            return render(request, 'store/register.html', {"error": error})

    # Возвратить страницу регистрации при GET запросе
    return render(request, 'store/register.html', {})


def login_page(request):
    '''
        Контроллер, отвечающий за логику:
        - отображения страницы логина
        - аутентификации пользователя
    '''
    if request.method == "GET":
        return render(request, "store/login.html", {})
    #if request.method == "POST":
    else:
        # Аутентификация пользователя при POST запросе
        username = request.POST.get("login", None)
        password = request.POST.get("password", None)
        user = authenticate(request, username=username, password=password)

        # Если пользователь существует и данные верны: перенаправить в страницу профиля
        if user:
            login(request, user)
            return redirect(reverse("store:store"))

        # Если данные неверны: возвратить сообщение о некорректных данных
        return render(request, "store/login.html", {"error": "Неправильный логин или пароль"})
    # else:
    # # Возвратить страницу логина при GET запросе
    #     return render(request, "main/login.html", {})
