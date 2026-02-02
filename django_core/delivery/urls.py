from django.urls import path, include
from .views import  * # Import your client views here
urlpatterns = [
    path('complete/', CompleteDelivery.as_view(), name='complete-delivery'),
]
