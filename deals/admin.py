from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import Deal, Manager, Salesperson

class ManagerInline(admin.StackedInline):
    model = Manager
    can_delete = False
    verbose_name_plural = 'Manager'

class SalespersonInline(admin.StackedInline):
    model = Salesperson
    can_delete = False
    verbose_name_plural = 'Salesperson'

class CustomUserAdmin(UserAdmin):
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        inline_instances = []
        if obj.groups.filter(name='Managers').exists():
            inline_instances.append(ManagerInline(self.model, self.admin_site))
        elif obj.groups.filter(name='Salespeople').exists():
            inline_instances.append(SalespersonInline(self.model, self.admin_site))
        return inline_instances

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields['groups'].initial = [Group.objects.get(name='Salespeople')]
        return form

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('recap_number', 'date', 'car_type',  'customer_name', 'vehicle_model', 'created_at')
    list_filter = ('car_type', 'created_at', 'date', 'salesperson', 'manager')
    search_fields = ('customer_name', 'stock_number')
    readonly_fields = ()
    
    def get_ordering(self, request):
        return ['-date', '-created_at']  # Order by creation date, newest first


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email')
    search_fields = ('user__username', 'user__email')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Salesperson)
class SalespersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email')
    search_fields = ('user__username', 'user__email')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'