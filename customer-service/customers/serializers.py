from rest_framework import serializers
from .models import Address, Customer


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['line1', 'line2', 'city', 'state', 'postal_code', 'country']


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='fullname.full_name', read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'address', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'password']

    def create(self, validated_data):
        customer = Customer.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )
        return customer


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UpdateAddressSerializer(serializers.Serializer):
    line1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=120, required=False, allow_blank=True)
    state = serializers.CharField(max_length=120, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    country = serializers.CharField(max_length=120, required=False, allow_blank=True)


class UpdateCustomerProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=False)
    address = AddressSerializer(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('No data provided to update.')
        return attrs
