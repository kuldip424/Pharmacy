from django.urls import path
from .views import indexView ,RegistrationView,loginView,productView,ForgotView,productDetail,cartView,plusView,minusView,removeView,checkoutView,orderHistory,orderDetail,invoiceView,CancelOrderView,searchView,addToCartView,logoutView,orderConfirmation
urlpatterns = [
    path('',indexView,name='index'),
    path('register/',RegistrationView,name='register'),
    path('login/',loginView,name='login'),
    path('logout/',logoutView,name='logout'),
    path('product/',productView,name='product'),
    path('product_category/<int:id>/',productView,name='product_category'),
    path('forgot/',ForgotView,name='forgot'),
    path('detail/<int:id>/',productDetail,name='detail'),
    path('cart/',cartView,name='cart'),
    path('plus/<int:id>/',plusView,name='plus'),
    path('minus/<int:id>/',minusView,name='minus'),
    path('remove/<int:id>/',removeView,name='remove'),
    path('checkout/',checkoutView,name='checkout'),
    path('history/',orderHistory,name='history'),
    path('orderdetail/<int:id>/',orderDetail,name='orderdetail'),
    path('invoice/<int:id>/',invoiceView,name='invoice'),
    path('cancle/<int:id>/',CancelOrderView,name='cancle'),
    path('search/',searchView,name='search'),
    path('addtocart/<int:id>/',addToCartView,name='addtocart'),
    path('confirm/<int:id>/',orderConfirmation,name='confirm'),
]
