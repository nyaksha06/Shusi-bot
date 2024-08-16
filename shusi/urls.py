from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', views.bot,name='bot'),
    path('send_message/', views.send_message, name='send_message'),
    path('', views.home,name= 'home'),
]
