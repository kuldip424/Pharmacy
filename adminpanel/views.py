from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.models import ProductModel, OrderModel, CategoryModel, CartModel, SupplierModel, orderItemModel
from .models import UserModel
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.contrib.auth.hashers import check_password
from .decorators import admin_login_required, admin_only
import csv
from django.http import HttpResponse
# Create your views here.

def userlogin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = UserModel.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id']=user.id
                request.session['role']=user.role
                return redirect('dashboard')
            else:
                return render(request,'userlogin.html',{'error':'Invalid Email or Password'})
        except UserModel.DoesNotExist:
            return render(request,'userlogin.html',{'error':'Invalid Email or Password'})
        except Exception as e:
            return render(request,'userlogin.html',{'error':'An unexpected error occurred'})
    return render(request,'userlogin.html')

def admin_logout(request):
    request.session.flush()
    messages.success(request, "Logged out from Admin Panel.")
    return redirect('userlogin')

@admin_login_required
def dashboardView(request):
    role = request.session.get('role')
    total_drug = ProductModel.objects.count()
    low_stock_count = ProductModel.objects.filter(stock__lte=5).count()
    low_stock_list = ProductModel.objects.filter(stock__lte=5)[:5]
    
    expired_count = ProductModel.objects.filter(expiry_date__lt=now().date()).count()
    expired_list = ProductModel.objects.filter(expiry_date__lt=now().date())[:5]
    
    today = now()
    monthly_sales = OrderModel.objects.filter(
        datetime__year=today.year,
        datetime__month=today.month
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Use OrderModel and orderItemModel to calculate profit for the current month
    monthly_orders = OrderModel.objects.filter(datetime__year=today.year, datetime__month=today.month)
    monthly_profit = 0
    for order in monthly_orders:
        for item in orderItemModel.objects.filter(order=order):
             monthly_profit += item.price - (item.qty * item.product.buy_price)

    recent_orders = OrderModel.objects.select_related('user').order_by('-id')[:5]
    products = ProductModel.objects.all()
    product_names = [p.name for p in products]
    product_stock = [p.stock for p in products]
    
    return render(request, 'dashboard.html', {'role':role,
                                              'total_drug':total_drug,
                                              'low_stock':low_stock_count,
                                              'low_stock_list':low_stock_list,
                                              'expired_count':expired_count,
                                              'expired_list':expired_list,
                                              'monthly_sales':monthly_sales,
                                              'monthly_profit':monthly_profit,
                                              'recent_orders':recent_orders,
                                              'product_names':product_names,
                                              'product_stock':product_stock
                                              })
    
    
@admin_login_required
def lowStockView(request):
    low_stock = ProductModel.objects.filter(stock__lte=5)
    return render(request, 'low_stock.html', {'products':low_stock})

@admin_login_required
def inventoryView(request):
    product_list = ProductModel.objects.all().order_by('id')
    cat = CategoryModel.objects.all()
    
    paginator = Paginator(product_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory.html', {'product': page_obj, 'cat': cat, 'page_obj': page_obj})

@admin_only
def add_product(request):
    cat = CategoryModel.objects.all()
    suppliers = SupplierModel.objects.all()
    if request.method == 'POST':
        add = ProductModel()
        add.name = request.POST['name']
        add.image = request.FILES['image']
        add.price = request.POST['price']
        add.buy_price = request.POST['buy_price']
        add.stock = request.POST['stock']
        add.description = request.POST['description']
        add.categories = CategoryModel.objects.get(id=request.POST['category'])
        
        supplier_id = request.POST.get('supplier')
        if supplier_id:
            add.supplier = SupplierModel.objects.get(id=supplier_id)
            
        add.manufacture_date = request.POST['manufacture_date']
        add.expiry_date = request.POST['expiry_date']
        add.save()
        messages.success(request, "Product added successfully.")
        return redirect('inventory')
    return render(request, 'addproduct.html', {'cat': cat, 'suppliers': suppliers})

from django.shortcuts import get_object_or_404, redirect, render


@admin_only
def edit_product(request, id):
    product = get_object_or_404(ProductModel, id=id)
    cat = CategoryModel.objects.all()
    suppliers = SupplierModel.objects.all()

    if request.method == 'POST':
        product.name = request.POST['name']
        if 'image' in request.FILES:
            product.image = request.FILES['image']  
        product.categories = CategoryModel.objects.get(id=request.POST['category'])
        
        supplier_id = request.POST.get('supplier')
        if supplier_id:
            product.supplier = SupplierModel.objects.get(id=supplier_id)
        else:
            product.supplier = None
            
        product.stock = request.POST['stock']
        product.price = request.POST['price']
        product.buy_price = request.POST['buy_price']
        product.description = request.POST['description']
        product.manufacture_date = request.POST['manufacture_date']
        product.expiry_date = request.POST['expiry_date']
        product.save()
        return redirect('inventory')

    return render(request, 'editeproduct.html', {'product': product, 'cat': cat, 'suppliers': suppliers})

@admin_only
def delete_product(request, id):
    product = get_object_or_404(ProductModel, id=id)
    product.delete()
    return redirect('inventory')

from django.utils.timezone import now
from django.db.models import Sum
@admin_only
def salesView(request):
    today = now().date()
    month = today.month
    year = today.year
    
    # Aggregates for Summary
    today_sales = OrderModel.objects.filter(datetime__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0
    month_sales = OrderModel.objects.filter(datetime__year=year, datetime__month=month).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Date Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    orders_list = OrderModel.objects.all().order_by('-datetime')
    if start_date and end_date:
        orders_list = orders_list.filter(datetime__date__range=[start_date, end_date])
    
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_items = orderItemModel.objects.filter(order_id__in=page_obj.object_list.values_list('id', flat=True))
    
    # Top Selling Drugs logic
    monthly_order_ids = OrderModel.objects.filter(
        datetime__month=month,
        datetime__year=year
    ).values_list('id', flat=True)

    top_selling = orderItemModel.objects.filter(
        order_id__in=monthly_order_ids
    ).values('product__name').annotate(
        total_qty=Sum('qty')
    ).order_by('-total_qty')[:5]
    
    context = {
        'order': page_obj,
        'today_sales': today_sales,
        'month_sales': month_sales,
        'cart_items': cart_items,
        'top_selling': top_selling,
        'page_obj': page_obj
    }
    return render(request, 'sales.html', context)

@admin_only
def export_sales_csv(request):
    today = now().date()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_records_{today.strftime("%Y_%m")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Customer', 'Products', 'Transaction ID', 'Total Price', 'Status', 'Payment Status'])

    orders = OrderModel.objects.filter(
        datetime__year=today.year, 
        datetime__month=today.month
    ).order_by('-datetime')

    for order in orders:
        items = orderItemModel.objects.filter(order=order)
        product_list = ", ".join([f"{item.product.name} (x{item.qty})" for item in items])
        writer.writerow([
            order.datetime.strftime("%Y-%m-%d %H:%M:%S"),
            order.name,
            product_list,
            order.transaction or "N/A",
            order.total_price,
            order.status,
            order.payment_status
        ])

    return response

@admin_only
def export_low_stock_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="low_stock_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Drug Name', 'Current Stock', 'Category', 'Supplier', 'Expiry Date'])

    low_stock_products = ProductModel.objects.filter(stock__lt=10).order_by('stock')

    for product in low_stock_products:
        writer.writerow([
            product.name,
            product.stock,
            product.categories.name if product.categories else "N/A",
            product.supplier.name if product.supplier else "N/A",
            product.expiry_date
        ])

    return response

@admin_only
def export_expired_drugs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expired_drugs_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Drug Name', 'Expiry Date', 'Current Stock', 'Supplier'])

    expired_products = ProductModel.objects.filter(expiry_date__lt=now().date()).order_by('expiry_date')

    for product in expired_products:
        writer.writerow([
            product.name,
            product.expiry_date,
            product.stock,
            product.supplier.name if product.supplier else "N/A"
        ])

    return response

@admin_only
def export_upcoming_expiry_csv(request):
    today = now().date()
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="upcoming_expiry_{next_year}_{next_month:02d}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Drug Name', 'Expiry Date', 'Current Stock', 'Supplier'])

    upcoming_expiry = ProductModel.objects.filter(
        expiry_date__year=next_year,
        expiry_date__month=next_month
    ).order_by('expiry_date')

    for product in upcoming_expiry:
        writer.writerow([
            product.name,
            product.expiry_date,
            product.stock,
            product.supplier.name if product.supplier else "N/A"
        ])

    return response

@admin_only
def update_order(request, id):
    order = get_object_or_404(OrderModel, id=id)
    if request.method == 'POST':
        status = request.POST.get('status')
        payment_status = request.POST.get('payment_status')
        if status:
            order.status = status
        if payment_status:
            order.payment_status = payment_status
        order.save()
        messages.success(request, f"Order #{id} updated.")
    return redirect('sales')

@admin_login_required
def customersView(request):
    customers_list = OrderModel.objects.values('user__name', 'user__email', 'mobile').annotate(
        total_spent=Sum('total_price'),
        order_count=Count('id')
    ).order_by('-total_spent')
    
    q = request.GET.get('q')
    if q:
        customers_list = customers_list.filter(
            Q(user__name__icontains=q) |
            Q(mobile__icontains=q)
        )
    
    paginator = Paginator(customers_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'customers.html', {'customers': page_obj, 'page_obj': page_obj})

@admin_login_required
def debtorsView(request):
    debtors_list = OrderModel.objects.filter(payment_status='PENDING').order_by('-datetime')
    
    paginator = Paginator(debtors_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'debators.html', {'debtors': page_obj, 'page_obj': page_obj})

@admin_login_required
def alertsView(request):
    low_stock = ProductModel.objects.filter(stock__lt=10)
    expired = ProductModel.objects.filter(expiry_date__lt=timezone.now().date())
    return render(request, 'alerts.html', {
        'low_stock': low_stock,
        'expired': expired,
    })

@admin_only
def add_category(request):
    categories = CategoryModel.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            CategoryModel.objects.create(name=name)
            messages.success(request, f"Category '{name}' added successfully.")
            return redirect('add_category')
    return render(request, 'addcategory.html', {'categories': categories})

@admin_only
def delete_category(request, id):
    category = get_object_or_404(CategoryModel, id=id)
    category.delete()
    return redirect('add_category')
@admin_only
def suppliersView(request):
    suppliers_list = SupplierModel.objects.all().order_by('id')
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        SupplierModel.objects.create(
            name=name, contact_person=contact, 
            email=email, mobile=mobile, address=address
        )
        messages.success(request, f"Supplier '{name}' added successfully.")
        return redirect('suppliers')
        
    paginator = Paginator(suppliers_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'suppliers.html', {'suppliers': page_obj, 'page_obj': page_obj})

@admin_only
def delete_supplier(request, id):
    supplier = get_object_or_404(SupplierModel, id=id)
    supplier.delete()
    messages.success(request, "Supplier deleted.")
    return redirect('suppliers')
    
    
    
    