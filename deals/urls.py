from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('used_car_deals/', views.used_car_deals, name='used_car_deals'),

    
    path('deals/', views.deal_list, name='deal_list'),
    path('deals/new/', views.new_car_deals, name='new_car_deals'),
    path('deals/used/', views.used_car_deals, name='used_car_deals'),

    path('deals-by-date/', views.deals_by_date, name='deals_by_date'),
    path('search/', views.search_deals, name='search_deals'),

    path('deals/<int:pk>/', views.deal_detail, name='deal_detail'),
    path('deals/create/', views.deal_create, name='deal_create'),
    path('deals/<int:pk>/update/', views.deal_update, name='deal_update'),
    path('daily-deals/', views.daily_deals, name='daily_deals'),
    path('monthly-deals/', views.monthly_deals, name='monthly_deals'),

    path('salespeople/', views.salesperson_list, name='salesperson_list'),
    path('salespeople/create/', views.create_salesperson, name='create_salesperson'),
    path('managers/', views.manager_list, name='manager_list'),
    path('managers/create/', views.create_manager, name='create_manager'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
]