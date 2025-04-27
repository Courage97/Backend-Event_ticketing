from rest_framework import serializers
from .models import VendorService, VendorBooking, EventVendorRequest


# ✅ Vendor Service Serializer
class VendorServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorService
        fields = '__all__'
        read_only_fields = ['vendor', 'created_at']


# ✅ Booking Serializer (used during creation)
class VendorBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBooking
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at']


# ✅ Display-friendly Booking Serializer (used for user history or admin view)
class MyVendorBookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.service_name', read_only=True)
    business_name = serializers.CharField(source='service.business_name', read_only=True)
    service_vendor = serializers.CharField(source='service.vendor.username', read_only=True)

    class Meta:
        model = VendorBooking
        fields = ['id', 'business_name', 'service_name', 'service_vendor', 'date', 'time', 'status', 'created_at']


# ✅ Event-to-Vendor Linking Serializer
class EventVendorRequestSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='vendor_service.business_name', read_only=True)
    service_name = serializers.CharField(source='vendor_service.service_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventVendorRequest
        fields = '__all__'
        read_only_fields = ['organizer', 'status', 'created_at']
