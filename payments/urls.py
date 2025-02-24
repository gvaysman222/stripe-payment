from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),

    path('item/<int:id>/', views.item_detail, name='item_detail'),
    path('buy/<int:id>/', views.create_checkout_session, name='create_checkout_session'),

    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path('order/pay/<int:id>/', views.create_order_payment_intent, name='create_order_payment_intent'),

    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),

    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
]
