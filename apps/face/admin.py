from django.contrib import admin

from .models import UserRegistration, CheckIn


class UserRegistrationAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "participation_role","email", "phone"]
    list_display = ["first_name", "last_name", "participation_role", "user_photo"]

class CheckInAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ["user", "timestamp"]


admin.site.site_header = "User Registration Panel"
admin.site.site_title = "User Registration Panel"
admin.site.register(UserRegistration, UserRegistrationAdmin)
admin.site.register(CheckIn, CheckInAdmin)
