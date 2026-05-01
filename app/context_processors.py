from .models import CartModel, RegistrationModel
from django.db.models import Sum

def cart_count(request):
    is_login = 'login' in request.session
    count = 0
    if is_login:
        try:
            user = RegistrationModel.objects.get(email=request.session['login'])
            # Sum up total quantities in the database cart
            result = CartModel.objects.filter(user=user, order_id=0).aggregate(total_qty=Sum('qty'))
            count = result['total_qty'] or 0
        except RegistrationModel.DoesNotExist:
            pass
    else:
        # Sum up total quantities in the guest session cart
        guest_cart = request.session.get('guest_cart', [])
        count = sum(item.get('qty', 0) for item in guest_cart)
    
    return {
        'cart_count': count,
        'is_login': is_login
    }

