from django.contrib import admin
from .models import CovidData

@admin.register(CovidData)
class CovidDataAdmin(admin.ModelAdmin):
    """
    Admin interface for COVID data management
    """
    list_display = ('state', 'confirmed', 'active', 'recovered', 'deaths', 'recovery_rate', 'death_rate')
    list_filter = ('state',)
    search_fields = ('state',)
    ordering = ('-confirmed',)
    
    # Make calculated fields readonly
    readonly_fields = ('recovery_rate', 'death_rate', 'active_rate')
    
    # Organize fields in the edit form
    fieldsets = (
        ('State Information', {
            'fields': ('state',)
        }),
        ('Case Numbers', {
            'fields': ('confirmed', 'active', 'recovered', 'deaths'),
            'description': 'Enter the number of cases for each category'
        }),
        ('Calculated Rates (%)', {
            'fields': ('recovery_rate', 'death_rate', 'active_rate'),
            'classes': ('collapse',),
            'description': 'These are automatically calculated'
        }),
    )
    
    # Custom actions
    actions = ['reset_active_cases']
    
    def reset_active_cases(self, request, queryset):
        """Custom admin action to reset active cases to 0"""
        updated = queryset.update(active=0)
        self.message_user(request, f'{updated} states had their active cases reset to 0.')
    reset_active_cases.short_description = "Reset active cases to 0"