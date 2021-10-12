from django.contrib import admin
from .models import Bar, Event, Address, Schedule, Game


class SchedulesInline(admin.TabularInline):
    model = Schedule


class AddressInline(admin.TabularInline):
    model = Address


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    inlines = [
        AddressInline,
        SchedulesInline
    ]

    readonly_fields = [
        'schedule'
    ]


for model in (Event, Address, Schedule, Game):
    admin.site.register(model)
