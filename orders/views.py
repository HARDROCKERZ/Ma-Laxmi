from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from carts.models import Cart, CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
import math
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
# stripe
import stripe
from django.views import View
from django.conf import settings
from carts.models import Current_User


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class create_checkout_session(View):
    def post(self, request, *args, **kwargs):
        total = 0
        quantity = 0
        cart_items = CartItem.objects.filter(user=request.user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')
        grand_total = 0
        tax = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (18 * total)/100
        grand_total = math.ceil(total+tax)*100
        host = request.get_host()

        order_id = request.POST.get('order-id')
        order = Order.objects.get(user=request.user, is_ordered=False)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',
                        'unit_amount': grand_total,
                        'product_data': {
                            'name': order.order_number,
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'product_id': order.order_number,
            },
            mode='payment',
            success_url='http://{}{}'.format(host, reverse('dashboard')),
            cancel_url='http://{}{}'.format(host, reverse('home')),
        )
        return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session['customer_details']['email']
        order_number = session['metadata']['product_id']
        total = session['amount_total']
        status = session['payment_status']
        transaction_id = session['id']

        user_database = Current_User.current_user_model

        # store transaction details
        order = Order.objects.get(is_ordered=False, order_number=order_number)
        payment = Payment(
            user=user_database,
            payment_id=transaction_id,
            payment_method='Stripe',
            amount_paid=total,
            status=status,
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        try:
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_received_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = customer_email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
        except ObjectDoesNotExist:
            pass

        cart_items = CartItem.objects.filter(user=user_database)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order = order
            orderproduct.payment = payment
            orderproduct.user = user_database
            orderproduct.product = item.product
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()
            # reduce stock
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=user_database).delete()
        # print(session)

    # Passed signature verification
    return HttpResponse(status=200)

#cash on delivery
def cod(request):
    order = Order.objects.get(user=request.user, is_ordered=False)
    # store transaction details
    payment = Payment(
        user=request.user,
        payment_id=order.order_number,
        # payment_method=body['payment_method'],
        payment_method='Cash',
        amount_paid=order.order_total,
    )
    order.status='Cash'
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # after order changes
    # send email order
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        # Reduce stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    # clear cart
    CartItem.objects.filter(user=request.user).delete()
    # send order email
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    # redirect data
    # data = {
    #     'order_number': order.order_number,
    #     'transID': payment.payment_id,
    # }
    # return JsonResponse(data)
    return redirect('dashboard')


# def fulfill_order(request):
# def create_checkout_session(request, total=0, quantity=0):
#     cart_items = CartItem.objects.filter(user=request.user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('store')
#     grand_total = 0
#     tax = 0
#     for cart_item in cart_items:
#         total += (cart_item.product.price * cart_item.quantity)
#         quantity += cart_item.quantity
#     tax = (18 * total)/100
#     grand_total = math.ceil(total+tax)*100

#     host = request.get_host()
#     checkout_session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=[
#             {
#                 'price_data': {
#                     'currency': 'inr',
#                     'unit_amount': grand_total,
#                     'product_data': {
#                         'name': 'Total',
#                     },
#                 },
#                 'quantity': 1,
#             },
#         ],
#         mode='payment',
#         success_url='http://{}{}'.format(host, reverse('dashboard')),
#         cancel_url='http://{}{}'.format(host, reverse('dashboard')),
#     )
#     return redirect(checkout_session.url, code=303)


# paypal
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body['orderID'])
    # store transaction details
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        # payment_method=body['payment_method'],
        payment_method='Paypal',
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # after order changes
    # send email order
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        # Reduce stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    # clear cart
    CartItem.objects.filter(user=request.user).delete()
    # send order email
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    # redirect data
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user
    Current_User.current_user_model = current_user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (18 * total)/100
    grand_total = round(total + tax, 2)
    convert = grand_total/72
    convert = round(convert,2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'convert':convert,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
