from django.urls import path, include
from .views import  * # Import your client views here
urlpatterns = [
    path('register/', RegisterClient.as_view(), name='register-client'),
    path('token/', TokenView.as_view(), name='token'),
]
