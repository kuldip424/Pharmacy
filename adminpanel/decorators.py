from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_login_required(view_func):
    """
    Decorator to ensure the user is logged into the admin panel session.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, "Please login to access the admin panel.")
            return redirect('userlogin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_only(view_func):
    """
    Decorator to ensure only users with 'admin' role can access the view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('userlogin')
        
        if request.session.get('role') != 'admin':
            messages.warning(request, "Access Denied: Admin privileges required.")
            return redirect('dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
