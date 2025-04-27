from rest_framework import serializers
from .models import Event
from .models import Ticket

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['organizer', 'is_paid', 'is_published', 'tickets_sold']

# Ticket booking serializer
class TicketBookingSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    

class MyTicketSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateTimeField(source='event.start_date', read_only=True)
    event_location = serializers.CharField(source='event.location', read_only=True)
    event_flyer = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id',
            'event_title',
            'event_date',
            'event_location',
            'event_flyer',
            'quantity',
            'qr_code_url',
            'reference',
            'created_at'
        ]

    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None

    def get_event_flyer(self, obj):
        request = self.context.get('request')
        flyer = obj.event.flyer
        if flyer and request:
            return request.build_absolute_uri(flyer.url)
        return None
