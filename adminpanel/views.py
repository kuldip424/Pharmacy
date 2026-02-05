from django.shortcuts import render
from app.models import ProductModel,OrderModel,CategoryModel,CartModel
from django.utils.timezone import now
from django.db.models import Sum
from django.utils import timezone
# Create your views here.
def deshbordView(request):
    total_drug = ProductModel.objects.count()
    low_stock = ProductModel.objects.filter(stock__lte=5).count()
    expired_count = ProductModel.objects.filter(expiry_date__lt=now().date()).count()
    today = now()
    monthly_sales = OrderModel.objects.filter(
        datetime__year=today.year,
        datetime__month=today.month
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    recent_orders = OrderModel.objects.select_related('user').order_by('-id')[:5]
    products = ProductModel.objects.all()
    product_names = [p.name for p in products]
    product_stock = [p.stock for p in products]
    
    return render(request, 'deshboard.html', {'total_drug':total_drug,
                                              'low_stock':low_stock,
                                              'expired_count':expired_count,
                                              'monthly_sales':monthly_sales,
                                              'recent_orders':recent_orders,
                                              'product_names':product_names,
                                              'product_stock':product_stock
                                              })
    
    
def lowStockView(request):
    low_stock = ProductModel.objects.filter(stock__lte=5)
    return render(request, 'low_stock.html', {'products':low_stock})

def inventoryView(request):
    product = ProductModel.objects.all()
    cat = CategoryModel.objects.all()
    return render(request, 'inventory.html', {'product':product,'cat':cat})

from django.utils.timezone import now
from django.db.models import Sum
def salesView(request):
    today = now().date()
    month = today.month
    year = today.year
    today_orders = OrderModel.objects.filter(datetime__date=today)
    today_sales = today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    month_order = OrderModel.objects.filter(datetime__year = year,datetime__month=month)
    month_sales = month_order.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    order = OrderModel.objects.all().order_by('-datetime')
    cart_items = CartModel.objects.filter(order_id__in=order.values_list('id', flat=True))
    return render(request,'sales.html',{'order':order,'today_sales':today_sales,'month_sales':month_sales,'cart_items':cart_items})

from django.db.models import Q
def customersView(request):
    customer = OrderModel.objects.all().order_by('-datetime')
   
    q = request.GET.get('q')
    if q:
        customer = customer.filter(
            Q(name__icontains=q) |
            Q(mobile__icontains=q)
        )
    return render(request,'customers.html',{'customer':customer})

def debatorsView(request):
    return render(request, 'debators.html', {})

def alertsView(request):
    low_stock = ProductModel.objects.filter(stock__lt=10)
    expired = ProductModel.objects.filter(expiry_date__lt=timezone.now().date())
    return render(request, 'alerts.html', {
        'low_stock': low_stock,
        'expired': expired,
    })
    
    
    
    