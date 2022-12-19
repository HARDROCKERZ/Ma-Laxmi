from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt



urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    # #stripe
    path('create_checkout_session/',views.create_checkout_session.as_view(),name='create_checkout_session'),     
    path('webhook/stripe/',csrf_exempt(views.stripe_webhook),name='stripe_webhook'), 
    #cash on delivery
    path('cod/',views.cod,name='cod'),    
] 
