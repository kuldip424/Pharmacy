from django.urls import path
from .views import deshbordView,lowStockView,inventoryView,salesView,customersView,debatorsView,alertsView
urlpatterns = [
    path('',deshbordView,name='deshboard'),
    path('lowstock/',lowStockView,name='lowstock'),
    path('inventory/',inventoryView,name='inventory'),
    path('sales/',salesView,name='sales'),
    path('customers',customersView,name='customers'),
    path('debators/',debatorsView,name='debators'),
    path('alerts/',alertsView,name='alerts')
]
