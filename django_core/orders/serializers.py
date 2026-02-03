from rest_framework import serializers

class CustomerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.RegexField(r'^\d{10,15}$')

class ItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(min_value=1)
    weight = serializers.FloatField(required=False)
    is_fragile = serializers.BooleanField(default=False)

class LocationSerializer(serializers.Serializer):
    address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    contact_name = serializers.CharField()
    contact_phone = serializers.RegexField(r'^\d{10,15}$')

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Invalid latitude")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Invalid longitude")
        return value

class PaymentSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["COD", "ONLINE"])
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    customer = CustomerSerializer()
    items = ItemSerializer(many=True)
    pickup = LocationSerializer()
    drop = LocationSerializer()
    payment = PaymentSerializer()

    def validate_items(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one item required")
        return value
