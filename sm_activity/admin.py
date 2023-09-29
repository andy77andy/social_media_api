from django.contrib import admin

# Register your models here.
from sm_activity.models import Profile, Post, Comment


@admin.register(Profile)
class RouteAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class FlightAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class AirportAdmin(admin.ModelAdmin):
    pass
