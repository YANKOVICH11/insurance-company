from django.urls import path, re_path
from django.contrib.auth import views as auth_views_django
from . import views
from . import auth_views as custom_auth_views

urlpatterns = [
    # Основные страницы
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    re_path(r'^news/$', views.news_list, name='news_list'),
    re_path(r'^news/(?P<news_id>\d+)/$', views.news_detail, name='news_detail'),
    path('glossary/', views.glossary_list, name='glossary'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('promocodes/', views.promocodes_list, name='promocodes'),
    path('statistics/', views.statistics, name='statistics'),
    
    # Страховые продукты
    path('products/', views.insurance_products, name='insurance_products'),
    re_path(r'^products/(?P<insurance_id>\d+)/$', views.insurance_detail, name='insurance_detail'),
    
    # Аутентификация
    path('login/', auth_views_django.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', custom_auth_views.logout_view, name='logout'),
    path('register/', custom_auth_views.register, name='register'),
    
    # Личный кабинет
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buy-insurance/', views.buy_insurance, name='buy_insurance'),
    
    # Внешние API
    path('exchange-rates/', views.exchange_rate_view, name='exchange_rates'),
    path('weather/', views.weather_view, name='weather'),
    
    # CRUD операции
    re_path(r'^crud/branches/$', views.branch_list, name='branch_list'),
    re_path(r'^crud/branches/create/$', views.branch_create, name='branch_create'),
    re_path(r'^crud/branches/(?P<pk>\d+)/update/$', views.branch_update, name='branch_update'),
    re_path(r'^crud/branches/(?P<pk>\d+)/delete/$', views.branch_delete, name='branch_delete'),
    
    # Админ панель
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/contracts/', views.admin_contracts, name='admin_contracts'),
    path('admin/agents/', views.admin_agents, name='admin_agents'),
    path('admin/agents-income/', views.admin_agents_income, name='admin_agents_income'),
    
    # Для сотрудников
    path('employee/contracts/', views.employee_contracts, name='employee_contracts'),
]