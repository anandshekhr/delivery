from django.urls import path, include
from .views import  *
urlpatterns = [
    path('complete/', CompleteDelivery.as_view()),
    path("assign/", AssignDelivery.as_view()),
    path("respond/", RespondDelivery.as_view()),
    path("otp/generate/", GenerateDeliveryOTP.as_view()),
]
