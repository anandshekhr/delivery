from django.db import models

# Create your models here.
import uuid
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ("CREATED", "CREATED"),
        ("ASSIGNED", "ASSIGNED"),
        ("IN_TRANSIT", "IN_TRANSIT"),
        ("DELIVERED", "DELIVERED"),
        ("CANCELLED", "CANCELLED"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    client_id = models.UUIDField()
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    weight = models.FloatField(null=True, blank=True)
    is_fragile = models.BooleanField(default=False)

class Location(models.Model):
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)

class OrderRoute(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    pickup = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="pickups")
    drop = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="drops")

class Payment(models.Model):
    METHOD_CHOICES = (
        ("COD", "Cash On Delivery"),
        ("ONLINE", "Online"),
    )

    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("PAID", "PAID"),
        ("FAILED", "FAILED"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    cash_to_collect = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
