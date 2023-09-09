from .models import UserProfile
from django.contrib.sessions.models import Session
from .models import Addmonay_info
from django.contrib import admin


class Addmoney_infoAdmin(admin.ModelAdmin):
    list_display = ("user", "quantity", "Date", "Category", "add_money")


admin.site.register(Addmonay_info, Addmoney_infoAdmin)

admin.site.register(Session)
admin.site.register(UserProfile)
