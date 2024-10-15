from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, logout
from django.db import transaction, IntegrityError
from django.contrib.auth.forms import UserCreationForm
from .models import Deal, Salesperson, Manager
from .forms import DealForm, UserRegistrationForm, ManagerForm, SalespersonForm
import logging
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from decimal import Decimal
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime, timedelta


def search_deals(request):
    query = request.GET.get('q')
    if query:
        deals = Deal.objects.filter(
            Q(customer_name__icontains=query) |
            Q(vehicle_model__icontains=query) |
            Q(stock_number__icontains=query) |
            Q(salesperson__user__username__icontains=query) |
            Q(salesperson__user__first_name__icontains=query) |
            Q(salesperson__user__last_name__icontains=query) |
            Q(manager__user__username__icontains=query) |
            Q(manager__user__first_name__icontains=query) |
            Q(manager__user__last_name__icontains=query)

        )
    else:
        deals = Deal.objects.none()
    
    context = {
        'deals': deals,
        'query': query
    }
    return render(request, 'search_results.html', context)


logger = logging.getLogger(__name__)

# def dashboard(request):
#    return render(request, 'deals/dashboard.html')

@login_required
def daily_deals(request):
    date_str = request.GET.get('date')
    if date_str:
        date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = timezone.now().date()

    deals = Deal.objects.filter(date=date).values('id', 'customer_name', 'gross', 'car_type')
    deals_list = list(deals)
    for deal in deals_list:
        if isinstance(deal['gross'], Decimal):
            deal['gross'] = float(deal['gross'])
    
    return JsonResponse(deals_list, safe=False)

@login_required
def monthly_deals(request):
    date_str = request.GET.get('date')
    if date_str:
        date = timezone.datetime.strptime(date_str, '%Y-%m').date()
    else:
        date = timezone.now().date()

    start_date = date.replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    deals = Deal.objects.filter(date__range=[start_date, end_date]).values('id', 'customer_name', 'gross', 'car_type', 'date')
    deals_list = list(deals)
    for deal in deals_list:
        if isinstance(deal['gross'], Decimal):
            deal['gross'] = float(deal['gross'])
    
    return JsonResponse(deals_list, safe=False)


@login_required
def dashboard(request):

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)
    last_month_end = month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)


    # Daily statistics
    daily_stats = Deal.objects.filter(date=today).aggregate(
        total_gross=Sum('gross'),
        deal_count=Count('id'),
        avg_gross=Avg('gross')
    )
    yesterday_stats = Deal.objects.filter(date=yesterday).aggregate(total_gross=Sum('gross'))

    
    # Monthly statistics
    monthly_stats = Deal.objects.filter(date__gte=month_start, date__lte=today).aggregate(
        total_gross=Sum('gross'),
        deal_count=Count('id'),
        avg_gross=Avg('gross')
    )
    last_month_stats = Deal.objects.filter(date__gte=last_month_start, date__lte=last_month_end).aggregate(total_gross=Sum('gross'))


    # Calculate trends
    daily_trend = calculate_trend(daily_stats['total_gross'], yesterday_stats['total_gross'])
    monthly_trend = calculate_trend(monthly_stats['total_gross'], last_month_stats['total_gross'])


    # Get the date from the request, default to today
    date_str = request.GET.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = timezone.now().date()

    # Filter deals for the selected date
    deals = Deal.objects.filter(created_at__date=date)


    total_deals = deals.count()
    total_gross = deals.aggregate(Sum('gross'))['gross__sum'] or 0
    total_salespeople = Salesperson.objects.count()
    total_managers = Manager.objects.count()


    recent_deals = Deal.objects.order_by('-date')[:10]



    top_salespeople = Salesperson.objects.filter(deal__in=deals).annotate(
        deal_count=Count('deal')
    ).order_by('-deal_count')[:5]

    context = {
        'selected_date': date,
        'total_deals': total_deals,
        'total_gross': total_gross,
        'total_salespeople': total_salespeople,
        'total_managers': total_managers,
        'recent_deals': recent_deals,
        'top_salespeople': top_salespeople,
        'has_deals': deals.exists(),
        'daily_stats': daily_stats,
        'monthly_stats': monthly_stats,
        'daily_trend': daily_trend,
        'monthly_trend': monthly_trend,
        'today': today,

    }
    return render(request, 'deals/dashboard.html', context)

def calculate_trend(current, previous):
    if current is None:
        current = Decimal('0')
    if previous is None or previous == 0:
        return 0 if current == 0 else 100  # 100% increase if previous was 0
    return ((current - previous) / previous) * 100


def deals_by_date(request):
    selected_date = request.GET.get('date')
    view_type = request.GET.get('view_type', 'day')
    car_type = request.GET.get('car_type', 'ALL')
    
    if selected_date:
        selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()
    
    if view_type == 'day':
        deals = Deal.objects.filter(date=selected_date)
        date_display = selected_date.strftime('%B %d, %Y')
    else:  # month view
        start_of_month = selected_date.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        deals = Deal.objects.filter(date__range=[start_of_month, end_of_month])
        date_display = selected_date.strftime('%B %Y')
    
    if car_type != 'ALL':
        deals = deals.filter(car_type=car_type)
    
    stats = calculate_stats(deals)
    
    context = {
        'selected_date': selected_date,
        'view_type': view_type,
        'car_type': car_type,
        'date_display': date_display,
        'deals': deals,
        'stats': stats,
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('deals_content.html', context)
        return HttpResponse(html)
    
    return render(request, 'deals_by_date.html', context)

def calculate_stats(deals):
    stats = deals.aggregate(
        total_gross=Sum('gross'),
        avg_gross=Avg('gross'),
        deal_count=Count('id'),
        new_car_count=Count('id', filter=Q(car_type=Deal.NEW_CAR)),
        used_car_count=Count('id', filter=Q(car_type=Deal.USED_CAR))
    )

    stats['avg_gross'] = stats['avg_gross'] or 0

    return stats


def calculate_stats(deals):
    stats = deals.aggregate(
        total_gross=Sum('gross'),
        avg_gross=Avg('gross'),
        deal_count=Count('id'),
        new_car_count=Count('id', filter=Q(car_type=Deal.NEW_CAR)),
        used_car_count=Count('id', filter=Q(car_type=Deal.USED_CAR))
    )

    # Ensure avg_gross is 0 if there are no deals
    stats['avg_gross'] = stats['avg_gross'] or 0

    return stats



@login_required
def deal_list(request):
    return render(request, 'deals/deal_list.html')
@login_required
def new_car_deals(request):
    new_car_deals = Deal.objects.filter(car_type=Deal.NEW_CAR)
    context = {
        'deals': new_car_deals,
        'deal_type': 'New Car'
    }
    return render(request, 'deals/deal_type_list.html', context)
@login_required
def used_car_deals(request):
    used_car_deals = Deal.objects.filter(car_type=Deal.USED_CAR)
    context = {
        'deals': used_car_deals,
        'deal_type': 'Used Car'
    }
    return render(request, 'deals/deal_type_list.html', context)





@login_required
def deal_detail(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if not request.user.has_perm('deals.view_all_deals') and deal.salesperson.user != request.user:
        raise PermissionDenied
    return render(request, 'deals/deal_detail.html', {'deal': deal})

@login_required
def deal_create(request):
    if request.method == 'POST':
        form = DealForm(request.POST, user=request.user)
        if form.is_valid():
            deal = form.save(commit=False)
            if not request.user.has_perm('deals.view_all_deals'):
                deal.salesperson = Salesperson.objects.get(user=request.user)
            deal.save()
            return redirect('deal_detail', pk=deal.pk)
    else:
        form = DealForm(user=request.user)
    return render(request, 'deals/deal_form.html', {'form': form})

@login_required
def deal_update(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if not request.user.has_perm('deals.view_all_deals') and deal.salesperson.user != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = DealForm(request.POST, instance=deal, user=request.user)
        if form.is_valid():
            deal = form.save()
            return redirect('deal_detail', pk=deal.pk)
    else:
        form = DealForm(instance=deal, user=request.user)
    return render(request, 'deals/deal_form.html', {'form': form})



@login_required
@permission_required('deals.view_all_deals', raise_exception=True)
def manager_list(request):
    managers = Manager.objects.all()
    return render(request, 'deals/manager_list.html', {'managers': managers})

@login_required
@permission_required('deals.view_all_deals', raise_exception=True)
def salesperson_list(request):
    salespeople = Salesperson.objects.all()
    return render(request, 'deals/salesperson_list.html', {'salespeople': salespeople})

@login_required
@permission_required('deals.view_all_deals', raise_exception=True)
def create_manager(request):
    if request.method == 'POST':
        form = ManagerForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        firstname=form.cleaned_data['firstname'],
                        lastname=form.cleaned_data['lastname'],
                        password=form.cleaned_data['password']
                    )
                    manager = form.save(commit=False)
                    manager.user = user
                    manager.save()
                return redirect('manager_list')
            except Exception as e:
                logger.error(f"Error creating manager: {str(e)}")
                form.add_error(None, "An error occurred while creating the manager. Please try again.")
    else:
        form = ManagerForm()
    return render(request, 'deals/manager_form.html', {'form': form})

@login_required
@permission_required('deals.view_all_deals', raise_exception=True)
def create_salesperson(request):
    if request.method == 'POST':
        form = SalespersonForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        firstname=form.cleaned_data['firstname'],
                        lastname=form.cleaned_data['lastname'],
                        password=form.cleaned_data['password']
                    )
                    salesperson = form.save(commit=False)
                    salesperson.user = user
                    salesperson.save()
                return redirect('salesperson_list')
            except Exception as e:
                logger.error(f"Error creating salesperson: {str(e)}")
                form.add_error(None, "An error occurred while creating the salesperson. Please try again.")
    else:
        form = SalespersonForm()
    return render(request, 'deals/salesperson_form.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            if role == 'manager':
                Manager.objects.create(user=user)
                permission = Permission.objects.get(codename='view_all_deals')
                user.user_permissions.add(permission)
            else:
                Salesperson.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

#Logout redirect to log in
@require_http_methods(["GET", "POST"])
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')