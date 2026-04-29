from django.shortcuts import render,redirect,get_object_or_404
from .models import RegistrationModel,ProductModel,CategoryModel,ProductDetailModel,CartModel,OrderModel,orderItemModel
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
# Create your views here.
def indexView(request):
    is_login = 'login' in request.session
    product_list = ProductModel.objects.all().order_by('id')
    
    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'index.html', {'product': page_obj, 'is_login': is_login, 'page_obj': page_obj})
def aboutus(request):
    return render(request,'aboutus.html')
def RegistrationView(request):
    error = ""
    message = ""   
    data = request.session.get('reg_data', {})
    show_otp = request.session.get('show_otp', False)
    
    print(f"View called, method: {request.method}, show_otp: {show_otp}")  # Debug
    
    if request.method == 'POST':
       
        if 'send_otp' in request.POST:
            
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            mobile = request.POST.get('mobile', '').strip()
            password = request.POST.get('password', '')
            
            if not name or not email or not mobile or not password:
                error = "All fields are required"
            elif len(mobile) != 10 or not mobile.isdigit():
                error = "Mobile number must be 10 digits"
            elif len(password) < 6:
                error = "Password must be at least 6 characters"
            elif RegistrationModel.objects.filter(email = email).exists():
                error = "Email already registered"
            else:    
        
                otp = str(random.randint(100000, 999999))
            
            
                send_mail(
                    'Your OTP for Pharmacy Registration',
                    f'Your OTP is {otp}',
                    'gojiyaanita@gmail.com',
                    [email],
                    fail_silently=False,
                )
                
                
                request.session['otp'] = otp
                request.session['reg_data'] = {
                    'name': name,
                    'email': email,
                    'mobile': mobile,
                    'password': password
                }
                request.session['show_otp'] = True
                message = "OTP sent to your email"
                
        elif 'verify_otp' in request.POST:
            enter_otp = request.POST['otp']
            session_otp = request.session.get('otp')
            data = request.session.get('reg_data')
            if not enter_otp:
                error = "Please enter OTP"
            elif enter_otp != session_otp:
                error = "Invalid OTP"
            else:
            
                register = RegistrationModel()
                register.name = data['name']
                register.email = data['email']
                register.mobile = data['mobile']
                register.password = make_password(data['password'])
                register.otp = ''
                register.is_verified =  True
                register.save()
                del request.session['otp']
                del request.session['reg_data']
                del request.session['show_otp']
                messages.success(request, "Registration successful! You can now login.")

                return redirect('index')
            
            
    return render(request,'register.html',{'message':message,'error':error,'data':request.session.get('reg_data',{}),'show_otp': request.session.get('show_otp', False)})
    
def loginView(request):
    if request.method == 'POST':
        try:
            register = RegistrationModel.objects.get(email = request.POST['email'])
            if check_password(request.POST['password'], register.password):
                request.session['login'] = register.email
                
                # Guest Cart Merge Logic
                guest_cart = request.session.get('guest_cart', [])
                if guest_cart:
                    for item in guest_cart:
                        try:
                            product = ProductModel.objects.get(id=item['product_id'])
                            cart_item, created = CartModel.objects.get_or_create(
                                user=register, product=product, order_id=0,
                                defaults={'qty': 0, 'total_price': 0}
                            )
                            cart_item.qty += item['qty']
                            cart_item.total_price = cart_item.qty * product.price
                            cart_item.save()
                        except ProductModel.DoesNotExist:
                            continue
                    del request.session['guest_cart']
                
                messages.success(request, f"Welcome back, {register.name}!")
                return redirect('index')
            else:
                messages.error(request, "Incorrect password")
                return render(request, 'login.html', {})
        except RegistrationModel.DoesNotExist:
            messages.error(request, "Email not registered")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html', {})
    
def ForgotView(request):
    step = request.session.get('step', 1)

    if request.method == 'POST':

        # STEP 1
        if step == 1:
            email = request.POST.get('email', '').strip()

            if not email:
                messages.error(request, "Please enter your email")
            else:
                try:
                    user = RegistrationModel.objects.get(email=email)
                    otp = str(random.randint(100000, 999999))
                    user.otp = otp
                    user.save()

                    send_mail(
                        'Password Reset OTP',
                        f'Your OTP for password reset is: {otp}',
                        'gojiyaanita@gmail.com',
                        [email],
                        fail_silently=False
                    )

                    request.session['email'] = email
                    request.session['step'] = 2
                    step = 2
                    messages.success(request, "OTP sent to your email")

                except RegistrationModel.DoesNotExist:
                    messages.error(request, "Email not registered")

        # STEP 2
        elif step == 2:
            entered_otp = request.POST.get('otp', '').strip()
            email = request.session.get('email')   # ✅ FIX

            if not entered_otp:
                messages.error(request, "Please enter OTP")
            else:
                user = RegistrationModel.objects.get(email=email)
                if entered_otp == user.otp:
                    request.session['step'] = 3
                    step = 3
                    messages.success(request, "OTP verified! Enter your new password.")
                else:
                    messages.error(request, "Invalid OTP")

        # STEP 3
        elif step == 3:
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            email = request.session.get('email')   # ✅ FIX

            if not password or not confirm_password:
                messages.error(request, "Please enter new password and confirm password")
            elif password != confirm_password:
                messages.error(request, "Passwords do not match")
            elif len(password) < 6:
                messages.error(request, "Password must be at least 6 characters")
            else:
                user = RegistrationModel.objects.get(email=email)
                user.password = make_password(password)
                user.otp = ''
                user.save()

                del request.session['email']
                del request.session['step']

                messages.success(request, "Password reset successful! You can now login.")
                return redirect('login')

    return render(request, 'forgot.html', {'step': step})

def logoutView(request):
    request.session.pop('login', None)
    return redirect('login')
        
def productView(request,id = None):
    category_list = CategoryModel.objects.all()
    is_login = 'login' in request.session
    if id:
        product_list = ProductModel.objects.filter(categories=id).order_by('id')
    else:
        product_list = ProductModel.objects.all().order_by('id')
    
    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'product.html', {
        'product': page_obj,
        'category': category_list,
        'is_login': is_login,
        'page_obj': page_obj
    })

def productDetail(request,id):
    detail = ProductDetailModel.objects.get(product_id = id)
    if request.method == 'POST':
        if 'login' in request.session:
            user = RegistrationModel.objects.get(email = request.session['login'])
            product = ProductModel.objects.get(id = id)
            cart = CartModel()
            cart.user = user
            cart.product = product
            cart.total_price = product.price*int(request.POST['qty'])
            cart.qty = int(request.POST['qty'])
            cart.save()
            
            product.stock -= int(request.POST['qty'])
            product.save()
            return render(request,'detail.html',{'detail':detail,'is_login':True})    
    return render(request,'detail.html',{'detail':detail,'is_login':True})

def cartView(request):
    is_login = 'login' in request.session
    cart_items = []
    total = 0
    
    if is_login:
        user = RegistrationModel.objects.get(email=request.session['login'])
        db_cart = CartModel.objects.filter(user=user, order_id=0)
        for item in db_cart:
            cart_items.append(item)
            total += item.total_price
    else:
        # guest_cart is a list of dicts: [{'product_id': 1, 'qty': 2}, ...]
        guest_cart = request.session.get('guest_cart', [])
        for item in guest_cart:
            try:
                product = ProductModel.objects.get(id=item['product_id'])
                # Create a pseudo-cart object for the template
                price = product.price * item['qty']
                cart_items.append({
                    'product': product,
                    'qty': item['qty'],
                    'total_price': price,
                    'id': item['product_id'] # Use product_id as reference for plus/minus
                })
                total += price
            except ProductModel.DoesNotExist:
                continue

    msg = request.session.pop('outofstock', None)
    
    context = {
        'cart': cart_items,
        'data': True if cart_items else False,
        'outofstock': msg,
        'total': total,
        'is_login': is_login
    }
    return render(request, 'cart.html', context)
    
def plusView(request, id):
    if 'login' in request.session:
        cart = get_object_or_404(CartModel, id=id)
        product = cart.product
    else:
        # guest_cart handling
        guest_cart = request.session.get('guest_cart', [])
        if guest_cart is None: guest_cart = []
        found_item = None
        for item in guest_cart:
            if item['product_id'] == id:
                found_item = item
                break
        if not found_item: return redirect('cart')
        product = get_object_or_404(ProductModel, id=id)

    if product.stock < 1:
        request.session['outofstock'] = 'Product is out of stock'
    else:
        if 'login' in request.session:
            cart.qty += 1
            cart.total_price += product.price
            cart.save()
        else:
            found_item['qty'] += 1
            request.session.modified = True
        
        product.stock -= 1
        product.save()
    return redirect('cart')
    
def minusView(request, id):
    if 'login' in request.session:
        cart = get_object_or_404(CartModel, id=id)
        product = cart.product
    else:
        guest_cart = request.session.get('guest_cart', [])
        if guest_cart is None: guest_cart = []
        found_item = None
        for item in guest_cart:
            if item['product_id'] == id:
                found_item = item
                break
        if not found_item: return redirect('cart')
        product = get_object_or_404(ProductModel, id=id)

    # Perform removal or decrement
    should_delete = False
    if 'login' in request.session:
        if cart.qty <= 1:
            should_delete = True
            cart.delete()
        else:
            cart.qty -= 1
            cart.total_price -= product.price
            cart.save()
    else:
        if found_item['qty'] <= 1:
            should_delete = True
            guest_cart.remove(found_item)
            request.session['guest_cart'] = guest_cart
        else:
            found_item['qty'] -= 1
            request.session.modified = True

    product.stock += 1
    product.save()
    return redirect('cart')

def removeView(request, id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email=request.session['login'])
        cart = get_object_or_404(CartModel, id=id, user=user)
        cart.product.stock += cart.qty
        cart.product.save()
        cart.delete()
    else:
        guest_cart = request.session.get('guest_cart', [])
        if guest_cart is None: guest_cart = []
        for item in guest_cart:
            if item['product_id'] == id:
                product = get_object_or_404(ProductModel, id=id)
                product.stock += item['qty']
                product.save()
                guest_cart.remove(item)
                request.session['guest_cart'] = guest_cart
                break
    return redirect('cart')

def checkoutView(request):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        cart = CartModel.objects.filter(user = user,order_id=0)
        total = 0
        grant_total =0
        for i in cart:
            total += i.total_price
        grant_total=total+50
        request.session['amount'] = float(grant_total)
        if request.method == "POST":
            if request.POST['payment_method'] == 'COD':
                
                order = OrderModel.objects.create(
                    user=user,    
                    name=request.POST['name'],
                    mobile=request.POST['mobile'],
                    address=request.POST['add'],
                    city=request.POST['city'],
                    state=request.POST['state'],
                    zipcode=request.POST['zip'],
                    payment_mode="COD",
                    total_price=grant_total,
                    status="PLACED",
                    payment_status="PENDING"
                )
                for i in cart:
                    orderItemModel.objects.create(
                        order = order,
                        product = i.product,
                        qty = i.qty,
                        price = i.total_price
                    )
                    
                
                cart.delete()
                return redirect('confirm', id=order.id)
            else:
                request.session['amount'] = float(grant_total)
                request.session['name'] = request.POST['name']
                request.session['mobile'] = request.POST['mobile']
                request.session['address'] = request.POST['add']
                request.session['city'] = request.POST['city']
                request.session['state'] = request.POST['state']
                request.session['zipcode'] = request.POST['zip']
                request.session['amount'] = float(grant_total)
                
                return redirect('payment')

        return render(request, 'checkout.html', {'total':total,'grant_total':grant_total,'is_login':True})
    else:
        messages.info(request, "Please login to proceed with checkout.")
        return redirect('login')


from django.urls import reverse
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse

def payment(request):
    try:
        amount = request.session.get('amount')

        if not amount:
            messages.error(request, "Invalid payment amount.")
            return redirect('checkout')

        currency = 'INR'
        amount_paise = int(float(amount) * 100)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        print(f"DEBUG: Creating Razorpay Order - Amount: {amount_paise}, Currency: {currency}")
        
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': currency,
            'payment_capture': 1
        })

        razorpay_order_id = razorpay_order['id']
        print(f"DEBUG: Razorpay Order Created: {razorpay_order_id}")
        request.session['razorpay_order_id'] = razorpay_order_id

        callback_url = request.build_absolute_uri(reverse('payment_handler'))

        context = {
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': amount_paise,
            'razorpay_order_id': razorpay_order_id,
            'callback_url': callback_url,
            'currency': currency,
            'is_login': True
        }

        return render(request, 'payment.html', context)

    except Exception as e:
        print("ERROR IN PAYMENT:", e)
        messages.error(request, f"Payment failed to initialize: {str(e)}")
        return redirect('checkout')


@csrf_exempt
def payment_handler(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")

    try:
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        if not all([payment_id, razorpay_order_id, signature]):
            messages.error(request, "Payment data missing.")
            return redirect('checkout')

        # Verify Signature
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        client.utility.verify_payment_signature(params_dict)

        # Retrieve session data
        email = request.session.get('login')
        if not email:
            messages.error(request, "Session expired. Please login again.")
            return redirect('login')

        user = RegistrationModel.objects.get(email=email)
        cart = CartModel.objects.filter(user=user, order_id=0)

        if not cart.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        name = request.session.get('name')
        mobile = request.session.get('mobile')
        address = request.session.get('address')
        city = request.session.get('city')
        state = request.session.get('state')
        zipcode = request.session.get('zipcode')
        amount = request.session.get('amount')

        if not all([name, mobile, address, city, state, zipcode]):
            messages.error(request, "Missing delivery information.")
            return redirect('checkout')

        # Create Order
        order = OrderModel.objects.create(
            user=user,
            total_price=amount,
            name=name,
            mobile=mobile,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            payment_mode="Razorpay",
            status="PLACED",
            payment_status="PAID",
            transaction=payment_id
        )

        # Create Order Items
        for item in cart:
            orderItemModel.objects.create(
                order=order,
                product=item.product,
                qty=item.qty,
                price=item.total_price
            )

        # Clear cart
        cart.delete()

        # Clear session payment data
        keys_to_clear = ['name', 'mobile', 'address', 'city', 'state', 'zipcode', 'amount', 'razorpay_order_id']
        for key in keys_to_clear:
            request.session.pop(key, None)

        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect('confirm', id=order.id)

    except Exception as e:
        print("PAYMENT ERROR:", e)
        messages.error(request, f"Payment verification failed: {str(e)}")
        return redirect('checkout')

def orderHistory(request):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        order_list = OrderModel.objects.filter(user=user).order_by('-id')
        
        paginator = Paginator(order_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'history.html', {'order': page_obj, 'is_login': True, 'page_obj': page_obj})
    else:
        return redirect('login')
    
def orderDetail(request,id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        order = OrderModel.objects.get(id = id , user = user)
        items = orderItemModel.objects.filter(order_id=order.id)
        subtotal = 0
        for i in items:
            subtotal += i.price 
        # total = order.total_price + 50
        return render(request, 'order_detail.html', {'order':order,'total':order.total_price,'is_login':True,'items':items,'subtotal':subtotal})
    return redirect('login')    

def invoiceView(request,id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email=request.session['login'])
        order = OrderModel.objects.get(id=id, user=user)

        # Get all products of this order
        items = orderItemModel.objects.filter(order_id=order.id)

        # Calculate subtotal, shipping, tax, and total
        subtotal = 0
        for i in items:
            subtotal+=i.price
        shipping = 50
        tax = 0  # You can add tax calculation if needed
        total = subtotal + shipping + tax

        return render(request, 'invoice.html', {
            'order': order,
            'items': items,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'total': total,
            'is_login': True
        })
    return redirect('login')
    
def CancelOrderView(request, id):
    if 'login' in request.session:
        order = get_object_or_404(OrderModel, id=id)
        if order.status != 'DELIVERED' and order.status != 'CANCELLED':
            order.status = 'CANCELLED'
            order.save()
            
            # Restore stock for each item in the order
            items = orderItemModel.objects.filter(order=order)
            for item in items:
                item.product.stock += item.qty
                item.product.save()

        return redirect('history')
    else:
        return redirect('login')
    
def orderConfirmation(request, id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email=request.session['login'])
        order = OrderModel.objects.get(id=id, user=user)
        items = orderItemModel.objects.filter(order_id=order.id)

        # Calculate total
        subtotal = 0
        for i in items:
            subtotal+=i.price
        shipping = 50
        total = subtotal + shipping

        return render(request, 'order_confirmation.html', {
            'order': order,
            'items': items,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': total,
            'is_login': True
        })
    return redirect('login')
    
    
    
    
from django.db.models import Q

def searchView(request):
    query = request.GET.get('q')
    if query:
        product_list = ProductModel.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(categories__name__icontains=query)
        ).order_by('id')
    else:
        product_list = ProductModel.objects.all().order_by('id')
    
    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    category_list = CategoryModel.objects.all()
    is_login = 'login' in request.session
    
    return render(request, 'product.html', {
        'product': page_obj, 
        'category': category_list, 
        'is_login': is_login,
        'page_obj': page_obj
    })

def addToCartView(request, id):
    if request.method == 'POST':
        product = get_object_or_404(ProductModel, id=id)
        qty = int(request.POST.get('qty', 1))

        if product.stock < qty:
            request.session['outofstock'] = f"'{product.name}' is out of stock!"
            return redirect('product')

        if 'login' in request.session:
            user = RegistrationModel.objects.get(email=request.session['login'])
            cart_item, created = CartModel.objects.get_or_create(
                user=user, product=product, order_id=0,
                defaults={'qty': 0, 'total_price': 0}
            )
            cart_item.qty += qty
            cart_item.total_price = cart_item.qty * product.price
            cart_item.save()
        else:
            # Guest Cart Logic
            guest_cart = request.session.get('guest_cart', [])
            if guest_cart is None: guest_cart = []
            item_found = False
            for item in guest_cart:
                if item['product_id'] == id:
                    item['qty'] += qty
                    item_found = True
                    break
            if not item_found:
                guest_cart.append({'product_id': id, 'qty': qty})
            request.session['guest_cart'] = guest_cart

        product.stock -= qty
        product.save()
        return redirect('cart')
    return redirect('product')



