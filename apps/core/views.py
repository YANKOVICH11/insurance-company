import calendar
from datetime import datetime, date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from .models import *
from .forms import ReviewForm, InsuranceContractForm
import logging

logger = logging.getLogger(__name__)

def get_user_timezone(request):
    return request.session.get('user_timezone', 'Europe/Minsk')

def index(request):
    latest_news = News.objects.filter(is_published=True).first()
    insurance_types = InsuranceType.objects.all()[:6]
    branches = Branch.objects.all()[:3]
    
    now = datetime.now()
    cal = calendar.monthcalendar(now.year, now.month)
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    months_ru = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    month_name = months_ru[now.month]
    
    context = {
        'latest_news': latest_news,
        'insurance_types': insurance_types,
        'branches': branches,
        'calendar': cal,
        'weekdays': weekdays,
        'month_name': month_name,
        'year': now.year,
        'today': now.day,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
        'user_timezone': get_user_timezone(request),
    }
    logger.info("Главная страница загружена")
    return render(request, 'core/index.html', context)

def about(request):
    branches = Branch.objects.all()
    context = {'branches': branches, 'current_date': datetime.now().strftime('%d/%m/%Y')}
    return render(request, 'core/about.html', context)

def news_list(request):
    news = News.objects.filter(is_published=True).order_by('-published_date')
    context = {'news': news, 'current_date': datetime.now().strftime('%d/%m/%Y')}
    return render(request, 'core/news_list.html', context)

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'core/news_detail.html', {'news': news})

def glossary_list(request):
    terms = Glossary.objects.all().order_by('term')
    context = {'terms': terms, 'current_date': datetime.now().strftime('%d/%m/%Y')}
    return render(request, 'core/glossary.html', context)

def contacts(request):
    employees = Employee.objects.select_related('branch').all()
    return render(request, 'core/contacts.html', {'employees': employees})

def privacy(request):
    return render(request, 'core/privacy.html')

def vacancies(request):
    vacancies_list = Vacancy.objects.filter(is_active=True)
    context = {'vacancies': vacancies_list, 'current_date': datetime.now().strftime('%d/%m/%Y')}
    return render(request, 'core/vacancies.html', context)

def reviews_list(request):
    reviews = Review.objects.filter(is_approved=True).order_by('-date')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.client_name = request.user.username
            review.is_approved = True
            review.save()
            messages.success(request, "Спасибо за отзыв!")
            return redirect('reviews')
    else:
        form = ReviewForm()
    
    from django.db.models import Avg
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'reviews': reviews,
        'form': form,
        'avg_rating': avg_rating,
        'reviews_count': reviews.count(),
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/reviews.html', context)

def promocodes_list(request):
    active = PromoCode.objects.filter(status='active')
    archived = PromoCode.objects.filter(status='archived')
    return render(request, 'core/promocodes.html', {
        'active_promocodes': active,
        'archived_promocodes': archived,
    })

def statistics(request):
    from django.db.models import Count, Sum, Avg
    
    total_contracts = InsuranceContract.objects.count()
    total_clients = Client.objects.count()
    total_agents = InsuranceAgent.objects.filter(is_active=True).count()
    total_branches = Branch.objects.count()
    
    insurance_by_type = InsuranceContract.objects.values('insurance_type__name').annotate(
        count=Count('id'),
        total_sum=Sum('insurance_sum')
    )
    
    most_popular = insurance_by_type.order_by('-count').first()
    most_profitable = insurance_by_type.order_by('-total_sum').first()
    
    ages = []
    for client in Client.objects.all():
        ages.append(client.age)
    avg_age = sum(ages) / len(ages) if ages else 0
    ages_sorted = sorted(ages)
    median_age = ages_sorted[len(ages_sorted)//2] if ages_sorted else 0
    
    context = {
        'total_contracts': total_contracts,
        'total_clients': total_clients,
        'total_agents': total_agents,
        'total_branches': total_branches,
        'insurance_by_type': insurance_by_type,
        'most_popular': most_popular,
        'most_profitable': most_profitable,
        'avg_age': avg_age,
        'median_age': median_age,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/statistics.html', context)

@login_required
def dashboard(request):
    if request.user.user_type == 'client':
        try:
            client = Client.objects.get(user=request.user)
            contracts = InsuranceContract.objects.filter(client=client)
        except Client.DoesNotExist:
            client = None
            contracts = []
    else:
        client = None
        contracts = []
    return render(request, 'core/dashboard.html', {
        'client': client,
        'contracts': contracts,
    })

@login_required
def buy_insurance(request):
    if request.user.user_type != 'client':
        messages.error(request, "Только клиенты могут покупать страховку")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InsuranceContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            try:
                client = Client.objects.get(user=request.user)
                contract.client = client
            except Client.DoesNotExist:
                messages.error(request, "Профиль клиента не найден")
                return redirect('dashboard')
            
            agent = InsuranceAgent.objects.filter(is_active=True).first()
            if agent:
                contract.agent = agent
            contract.save()
            messages.success(request, "Договор успешно оформлен!")
            return redirect('dashboard')
    else:
        form = InsuranceContractForm()
    
    return render(request, 'core/buy_insurance.html', {'form': form})

def exchange_rate_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        response = requests.get('https://api.nbrb.by/exrates/rates?periodicity=0')
        rates = response.json()
        main_rates = [r for r in rates if r['Cur_Abbreviation'] in ['USD', 'EUR', 'RUB']]
    except:
        main_rates = []
    return render(request, 'core/exchange_rates.html', {'rates': main_rates})

def weather_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    weather_data = {
        'name': 'Минск',
        'main': {'temp': 5, 'humidity': 75},
        'weather': [{'description': 'облачно'}]
    }
    return render(request, 'core/weather.html', {'weather': weather_data})

def insurance_products(request):
    insurance_types = InsuranceType.objects.all()
    
    sample_sums = {
        "КАСКО": 50000,
        "ОСАГО": 5000,
        "Медицинское": 20000,
        "Имущество": 30000,
        "Жизнь": 25000,
    }
    
    products = []
    for ins in insurance_types:
        sample_sum = sample_sums.get(ins.name, 20000)
        yearly_payment = sample_sum * (ins.base_rate / 100)
        monthly_payment = yearly_payment / 12
        
        products.append({
            'type': ins,
            'sample_sum': sample_sum,
            'monthly_payment': monthly_payment,
            'yearly_payment': yearly_payment,
        })
    
    context = {
        'products': products,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/insurance_products.html', context)

def insurance_detail(request, insurance_id):
    insurance = get_object_or_404(InsuranceType, id=insurance_id)
    
    calculations = []
    amounts = [10000, 25000, 50000, 100000, 250000]
    for amount in amounts:
        yearly_payment = amount * (insurance.base_rate / 100)
        monthly_payment = yearly_payment / 12
        calculations.append({
            'amount': amount,
            'yearly': yearly_payment,
            'monthly': monthly_payment,
        })
    
    context = {
        'insurance': insurance,
        'calculations': calculations,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/insurance_detail.html', context)

# ==================== CRUD ДЛЯ ФИЛИАЛОВ ====================

def branch_list(request):
    branches = Branch.objects.all()
    return render(request, 'core/crud/branch_list.html', {'branches': branches})

def branch_create(request):
    if request.method == 'POST':
        branch = Branch(
            name=request.POST['name'],
            address=request.POST['address'],
            phone=request.POST['phone']
        )
        branch.save()
        messages.success(request, "Филиал создан")
        return redirect('branch_list')
    return render(request, 'core/crud/branch_form.html')

def branch_update(request, pk):
    branch = get_object_or_404(Branch, id=pk)
    if request.method == 'POST':
        branch.name = request.POST['name']
        branch.address = request.POST['address']
        branch.phone = request.POST['phone']
        branch.save()
        messages.success(request, "Филиал обновлен")
        return redirect('branch_list')
    return render(request, 'core/crud/branch_form.html', {'branch': branch})

def branch_delete(request, pk):
    branch = get_object_or_404(Branch, id=pk)
    if request.method == 'POST':
        branch.delete()
        messages.success(request, "Филиал удален")
        return redirect('branch_list')
    return render(request, 'core/crud/branch_confirm_delete.html', {'branch': branch})

# ==================== CRUD ДЛЯ СТРАХОВОК ====================

def insurance_type_list(request):
    """Список видов страхования (READ)"""
    insurance_types = InsuranceType.objects.all().order_by('id')
    return render(request, 'core/crud/insurance_type_list.html', {'insurance_types': insurance_types})

def insurance_type_create(request):
    """Создание вида страхования (CREATE)"""
    if request.method == 'POST':
        insurance_type = InsuranceType(
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            commission_percent=request.POST['commission_percent'],
            base_rate=request.POST['base_rate']
        )
        insurance_type.save()
        messages.success(request, "Вид страхования создан")
        return redirect('insurance_type_list')
    return render(request, 'core/crud/insurance_type_form.html')

def insurance_type_update(request, pk):
    """Редактирование вида страхования (UPDATE)"""
    insurance_type = get_object_or_404(InsuranceType, id=pk)
    if request.method == 'POST':
        insurance_type.name = request.POST['name']
        insurance_type.description = request.POST.get('description', '')
        insurance_type.commission_percent = request.POST['commission_percent']
        insurance_type.base_rate = request.POST['base_rate']
        insurance_type.save()
        messages.success(request, "Вид страхования обновлен")
        return redirect('insurance_type_list')
    return render(request, 'core/crud/insurance_type_form.html', {'insurance_type': insurance_type})

def insurance_type_delete(request, pk):
    """Удаление вида страхования (DELETE)"""
    insurance_type = get_object_or_404(InsuranceType, id=pk)
    if request.method == 'POST':
        insurance_type.delete()
        messages.success(request, "Вид страхования удален")
        return redirect('insurance_type_list')
    return render(request, 'core/crud/insurance_type_confirm_delete.html', {'insurance_type': insurance_type})

# ==================== АДМИН ПАНЕЛЬ (ОСТАЛЬНОЕ) ====================

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Доступ только для администратора")
        return redirect('index')
    
    from django.db.models import Count, Sum
    
    stats = {
        'total_branches': Branch.objects.count(),
        'total_agents': InsuranceAgent.objects.count(),
        'total_clients': Client.objects.count(),
        'total_contracts': InsuranceContract.objects.count(),
        'active_contracts': InsuranceContract.objects.filter(status='active').count(),
    }
    
    context = {
        'stats': stats,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/admin/dashboard.html', context)

@login_required
def admin_contracts(request):
    if not request.user.is_superuser:
        messages.error(request, "Доступ только для администратора")
        return redirect('index')
    
    contracts = InsuranceContract.objects.select_related('client', 'agent', 'insurance_type').all()
    context = {
        'contracts': contracts,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/admin/contracts.html', context)

@login_required
def admin_agents(request):
    if not request.user.is_superuser:
        messages.error(request, "Доступ только для администратора")
        return redirect('index')
    
    branches = Branch.objects.prefetch_related('agents').all()
    context = {
        'branches': branches,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/admin/agents.html', context)

@login_required
def admin_agents_income(request):
    if not request.user.is_superuser:
        messages.error(request, "Доступ только для администратора")
        return redirect('index')
    
    agents = InsuranceAgent.objects.filter(is_active=True)
    agents_data = []
    for agent in agents:
        contracts = agent.contracts.all()
        total_commission = sum(c.agent_commission for c in contracts)
        agents_data.append({
            'agent': agent,
            'contracts_count': contracts.count(),
            'total_commission': total_commission,
        })
    
    context = {
        'agents_data': agents_data,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/admin/agents_income.html', context)

@login_required
def employee_contracts(request):
    if request.user.user_type == 'client':
        messages.error(request, "Доступ только для сотрудников")
        return redirect('dashboard')
    
    contracts = InsuranceContract.objects.select_related('client', 'agent', 'insurance_type').all()
    context = {
        'contracts': contracts,
        'current_date': datetime.now().strftime('%d/%m/%Y'),
    }
    return render(request, 'core/employee/contracts.html', context)