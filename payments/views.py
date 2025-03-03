import os
import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from .models import Item, Order

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
base_url = os.getenv('BASE_URL')

@require_GET
def create_checkout_session(request, id):
    item = get_object_or_404(Item, pk=id)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': item.currency,
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                    'unit_amount': int(item.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{base_url}/success/',
            cancel_url=f'{base_url}/cancel/',
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_GET
def item_detail(request, id):
    item = get_object_or_404(Item, pk=id)
    return render(request, 'item_detail.html', {
        'item': item,
        'stripe_publishable_key': STRIPE_PUBLISHABLE_KEY,
    })


@require_GET
def success(request):
    return HttpResponse("Payment successful!")


@require_GET
def cancel(request):
    return HttpResponse("Payment canceled!")

@require_GET
def order_detail(request, id):
    order = get_object_or_404(Order, pk=id)
    if order.items.exists():
        currency = order.items.first().currency.lower()
    else:
        currency = 'usd'
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    return render(request, 'order_detail.html', {
        'order': order,
        'stripe_publishable_key': publishable_key,
    })


@require_GET
def create_order_payment_intent(request, id):
    order = get_object_or_404(Order, pk=id)
    amount_cents = int(order.total_amount() * 100)
    if order.items.exists():
        currency = order.items.first().currency.lower()
    else:
        currency = 'usd'
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
        )
        order.stripe_payment_intent_id = intent.id
        order.save()
        return JsonResponse({'client_secret': intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def add_to_cart(request, id):
    cart = request.session.get('cart', [])
    if id not in cart:
        cart.append(id)
    request.session['cart'] = cart
    return redirect('cart_view')


def cart_view(request):
    cart = request.session.get('cart', [])
    items = Item.objects.filter(id__in=cart)
    return render(request, 'cart.html', {
        'items': items,
        'stripe_publishable_key': STRIPE_PUBLISHABLE_KEY,
    })


def checkout_cart(request):
    cart = request.session.get('cart', [])
    if not cart:
        return HttpResponse("Your cart is empty.", status=400)
    items = Item.objects.filter(id__in=cart)
    order = Order.objects.create()
    order.items.set(items)
    order.save()
    request.session['cart'] = []
    return redirect('order_detail', id=order.id)

def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items, 'stripe_publishable_key': STRIPE_PUBLISHABLE_KEY})
