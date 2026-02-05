from django.shortcuts import render,redirect
from .models import RegistrationModel,ProductModel,CategoryModel,ProductDetailModel,CartModel,OrderModel
import random
from django.core.mail import send_mail
from django.contrib import messages
# Create your views here.
def indexView(request):
    if 'login' in request.session:
        product = ProductModel.objects.all()
        return render(request,'index.html',{'product':product,'is_login':True})
    else:
        return redirect('login')
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
                register.password = data['password']
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
            if register.password == request.POST['password']:
                request.session['login'] = register.email
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
                user.password = password
                user.otp = ''
                user.save()

                del request.session['email']
                del request.session['step']

                messages.success(request, "Password reset successful! You can now login.")
                return redirect('login')

    return render(request, 'forgot.html', {'step': step})

def logoutView(request):
    del request.session['login']
    return redirect('login')
        
def productView(request,id = None):
    category = CategoryModel.objects.all()
    if 'login' in request.session:
        if id:
            product = ProductModel.objects.filter(categories=id)
        else:
            product = ProductModel.objects.all()
        return render(request, 'product.html', {'product':product,'category':category,'is_login':True})
    else:
        return redirect('login')

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
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        cart = CartModel.objects.filter(user = user,order_id=0)
        total= 0
        for i in cart:
            total += i.total_price
        msg = None
        if 'outofstock' in request.session:
            msg = request.session['outofstock']
            del request.session['outofstock']
        if cart:
            return render(request, 'cart.html', {'cart':cart,'data':True,'outofstock': msg,'total':total,'is_login':True})
        return render(request, 'cart.html', {'cart':cart,'outofstock': msg,'is_login':True})
    else:
        return redirect('login')
    
def plusView(request,id):
    cart = CartModel.objects.get(id = id)
    product = cart.product
    if product.stock < 1:
        request.session['outofstock'] = 'Product is out of stock'
        return redirect('cart')
    else:
        cart.qty += 1
        cart.total_price += product.price
        cart.save()
        
        product.stock-=1
        product.save()
        return redirect('cart')
    
def minusView(request,id):
    cart = CartModel.objects.get(id = id)
    product = cart.product
    if cart.qty <=1:
        product.stock+=1
        product.save()
        cart.delete()
        return redirect('cart')
    
    cart.qty -= 1
    cart.total_price -= product.price
    cart.save()
    
    product.stock+=1
    product.save()
    return redirect('cart')

def removeView(request,id):
    if 'login' not in request.session:
        return redirect('login')
    user = RegistrationModel.objects.get(email=request.session['login'])
    cart = CartModel.objects.get(id = id,user=user)
    cart.product.stock += cart.qty
    cart.product.save()
    cart.delete()
    return redirect('cart')

def checkoutView(request):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        cart = CartModel.objects.filter(user = user,order_id=0)
        total = 0
        for i in cart:
            total += i.total_price
        grant_total=total+50
        
        if request.method == "POST":
            
            order = OrderModel()
            order.user = user
            order.name = request.POST['name']
            order.mobile = request.POST['mobile']
            order.address = request.POST['add']
            order.city = request.POST['city']
            order.state = request.POST['state']
            order.zipcode = request.POST['zip']
            order.payment_mode = request.POST['payment_method']
            order.total_price = grant_total
            order.save()
            for i in cart:
               # latest_id=OrderModel.objects.latest('id')
                i.order_id = order.id
                i.save()
            
            email_subject = f"Order Confirmation - #{order.id}"
            email_message = f"""
Hi {user.name},

Thank you for your order!

Order ID: {order.id}
Total: Rs. {grant_total}

Items Ordered:
"""
            for item in cart:
                email_message += f"- {item.product.name} x {item.qty} = Rs. {item.total_price}\n"

            email_message += f"""

Shipping Address:
{order.address}, {order.city}, {order.state} - {order.zipcode}

We will notify you when your order is shipped.

Thank you for shopping with us!
"""

            send_mail(
                email_subject,
                email_message,
                'gojiyaanita@gmail.com',  # From email
                [user.email],
                fail_silently=False
            )
                
            cart.delete()
            return redirect('confirm',id=order.id)
            
        return render(request, 'checkout.html', {'total':total,'grant_total':grant_total,'is_login':True})
    return redirect('login')
        
def orderHistory(request):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        order = OrderModel.objects.filter(user = user)
        cart_items = CartModel.objects.filter(order_id__in=order.values_list('id', flat=True))
        return render(request,'history.html',{'order':order,'is_login':True,'cart_items':cart_items})
    else:
        return redirect('login')
    
def orderDetail(request,id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email = request.session['login'])
        order = OrderModel.objects.get(id = id , user = user)
        items = CartModel.objects.filter(order_id=order.id)
        subtotal = 0
        for i in items:
            subtotal += i.total_price 
        # total = order.total_price + 50
        return render(request, 'order_detail.html', {'order':order,'total':order.total_price,'is_login':True,'items':items,'subtotal':subtotal})
    return redirect('login')    

def invoiceView(request,id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email=request.session['login'])
        order = OrderModel.objects.get(id=id, user=user)

        # Get all products of this order
        items = CartModel.objects.filter(order_id=order.id)

        # Calculate subtotal, shipping, tax, and total
        subtotal = sum(i.total_price for i in items)
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
        order = OrderModel.objects.get(id=id)
        if order.status != 'Delivered':
            order.status = 'Cancelled'
            order.save()
            
            order.product.stock+=order.qty
            order.product.save()

        return redirect('history')
    else:
        return redirect('login')
    
def orderConfirmation(request, id):
    if 'login' in request.session:
        user = RegistrationModel.objects.get(email=request.session['login'])
        order = OrderModel.objects.get(id=id, user=user)
        items = CartModel.objects.filter(order_id=order.id)

        # Calculate total
        subtotal = sum(i.total_price for i in items)
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
    q = request.GET.get('q')

    if q:
        pro = ProductModel.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(categories__name__icontains=q)
        )
    else:
        pro = ProductModel.objects.all()

    return render(request, 'product.html', {'pro': pro})

def addToCartView(request, id):
    if request.method == 'POST':
        if 'login' in request.session:
            user = RegistrationModel.objects.get(email=request.session['login'])
            product = ProductModel.objects.get(id=id)

            if product.stock < 1:
                request.session['outofstock'] = f"'{product.name}' is out of stock!"
                return redirect('product')

            # 🔹 check if product already in cart
            try:
                cart = CartModel.objects.get(user=user, product=product,order_id=0)
                cart.qty += 1
                cart.total_price = cart.qty * product.price
                cart.save()
            except CartModel.DoesNotExist:
                cart = CartModel()
                cart.user = user
                cart.product = product
                cart.qty = 1
                cart.total_price = product.price
                cart.save()

            product.stock -= 1
            product.save()

            return redirect('cart')
        else:
            return redirect('login')
    return redirect('product')
