from django.urls import path, include
from .views import  * # Import your order views here
urlpatterns = [
    path("create/", CreateOrder.as_view()),
]
