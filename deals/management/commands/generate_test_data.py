from django.core.management.base import BaseCommand
from django.utils import timezone
from deals.models import Deal, Manager, Salesperson
from django.contrib.auth.models import User
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generates test data for the Deal model'

    def add_arguments(self, parser):
        parser.add_argument('num_deals', type=int, help='The number of deals to create')

    def handle(self, *args, **options):
        num_deals = options['num_deals']

        # Create test users, managers, and salespeople if they don't exist
        if not User.objects.filter(username='testmanager').exists():
            manager_user = User.objects.create_user(username='testmanager', password='testpass')
            Manager.objects.create(user=manager_user)

        if not User.objects.filter(username='testsalesperson').exists():
            salesperson_user = User.objects.create_user(username='testsalesperson', password='testpass')
            Salesperson.objects.create(user=salesperson_user)

        manager = Manager.objects.first()
        salesperson = Salesperson.objects.first()

        # Generate deals
        for i in range(num_deals):
            date = timezone.now().date() - timedelta(days=random.randint(0, 60))
            car_type = random.choice([Deal.NEW_CAR, Deal.USED_CAR])
            gross = random.uniform(1000, 10000)

            Deal.objects.create(
                car_type=car_type,
                date=date,
                stock_number=f'STOCK{i+1}',
                customer_name=f'Customer {i+1}',
                manager=manager,
                salesperson=salesperson,
                gross=gross,
                has_trade=random.choice([True, False]),
                trade_make=random.choice(['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW']) if random.choice([True, False]) else None,
                trade_model=f'Model {random.randint(1, 10)}' if random.choice([True, False]) else None,
                trade_value=random.uniform(500, 5000) if random.choice([True, False]) else None,
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_deals} test deals'))