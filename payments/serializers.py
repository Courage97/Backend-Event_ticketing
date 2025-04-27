from .models import Transaction
from rest_framework import serializers
from events.models import Ticket

class TransactionSerializer(serializers.ModelSerializer):
    event_title = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'event_title', 'amount', 'transaction_type',
            'reference', 'verified', 'created_at'
        ]

    def get_event_title(self, obj):
        if obj.transaction_type == "ticket_purchase":
            try:
                ticket = Ticket.objects.filter(reference=obj.reference).first()
                return ticket.event.title if ticket else "N/A"
            except:
                return "N/A"
        return "Event Publishing"


# payments/serializers.py or wherever relevant

class TicketConfirmationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title')
    event_location = serializers.CharField(source='event.location')
    event_date = serializers.DateTimeField(source='event.start_date')
    amount_paid = serializers.SerializerMethodField()
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'event_title',
            'event_location',
            'event_date',
            'quantity',
            'amount_paid',
            'qr_code',
            'reference',
        ]

    def get_amount_paid(self, obj):
        return float(obj.event.ticket_price) * obj.quantity

    def get_qr_code(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None
