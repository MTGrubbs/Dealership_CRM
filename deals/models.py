from django.db import models
from django.contrib.auth.models import User, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Max



class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any additional fields specific to managers here

    def __str__(self):
        return self.user.username

class Salesperson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any additional fields specific to salespeople here

    def __str__(self):
        return self.user.username

class Deal(models.Model):

    NEW_CAR = 'NEW'
    USED_CAR = 'USED'
    CAR_TYPE_CHOICES = [
        (NEW_CAR, 'New Car'),
        (USED_CAR, 'Used Car'),
    ]

    # Deal fields
    car_type = models.CharField(
        max_length=4,
        choices=CAR_TYPE_CHOICES,
        default=USED_CAR,
    )
    recap_number = models.PositiveIntegerField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    stock_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=80)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True)
    salesperson = models.ForeignKey(Salesperson, on_delete=models.SET_NULL, null=True)
    gross = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Trade fields
    has_trade = models.BooleanField(default=False)
    trade_make = models.CharField(max_length=50, blank=True, null=True)
    trade_model = models.CharField(max_length=50, blank=True, null=True)
    trade_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.recap_number is None:  # Only set recap_number if it's not already set
            self.set_recap_number()
        super().save(*args, **kwargs)

    def set_recap_number(self):
        # Get the current month and year
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get the maximum recap number for the current month
        max_recap = Deal.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_start + timezone.timedelta(days=32),
            car_type=self.car_type
        ).aggregate(Max('recap_number'))['recap_number__max'] or 0

        # Find the first available number
        #all_numbers = set(Deal.objects.filter(
        #    created_at__gte=month_start,
        #    created_at__lt=month_start + timezone.timedelta(days=32),
        #    car_type=self.car_type
        #).values_list('recap_number', flat=True))

        # Get the maximum recap number for the current month and car type

        self.recap_number = max_recap + 1

    class Meta:
        ordering = ['-created_at']

        

class CustomPermissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_all_deals', 'Can view all deals'),
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.groups.filter(name='Managers').exists():
            Manager.objects.create(user=instance)
            instance.user_permissions.add(Permission.objects.get(codename='view_all_deals'))
        elif instance.groups.filter(name='Salespeople').exists():
            Salesperson.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.groups.filter(name='Managers').exists():
        Manager.objects.get_or_create(user=instance)
    elif instance.groups.filter(name='Salespeople').exists():
        Salesperson.objects.get_or_create(user=instance)