from django.http import HttpResponse
from django.shortcuts import redirect,render
from store.models import Product
from django.core.paginator import EmptyPage,Paginator,PageNotAnInteger


def home(request):
    # products = Product.objects.all().filter(is_available=True) Origional
    products = Product.objects.all().filter(is_available=True).order_by('?') # ? to get random products
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        # 'products':products, Origional
        'products':paged_products,
    }
    return render(request,'home.html',context)