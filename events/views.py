from rest_framework import generics, permissions
from .models import Event
from .serializers import EventSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Event
from .utils import initialize_paystack_transaction
from .utils import verify_paystack_transaction
from .serializers import TicketBookingSerializer
from rest_framework import status
from payments.utils import initialize_paystack_transaction
from payments.models import Transaction
from .models import Ticket
from django.shortcuts import get_object_or_404
from payments.models import Transaction
import requests
from django.conf import settings
from .serializers import MyTicketSerializer
from django.core.mail import EmailMessage
from payments.serializers import TicketConfirmationSerializer
from django.template.loader import render_to_string


class EventCreateView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


# Payment gateway initializing
class InitiateEventPaymentView(APIView):
    def post(self, request):
        event_id = request.data.get("event_id")
        event = get_object_or_404(Event, id=event_id, organizer=request.user)

        if event.is_paid:
            return Response({"message": "Event already paid for."}, status=400)

        amount_to_pay = 5000  # ₦50.00 to publish
        metadata = {
            "event_id": event.id,
            "user_id": request.user.id,
            "type": "event_publish"
        }

        # ✅ Define callback_url **inside** the function
        callback_url = f"{settings.FRONTEND_BASE_URL}/payment-success"

        paystack_response = initialize_paystack_transaction(
            email=request.user.email,
            amount=amount_to_pay,
            metadata=metadata,
            callback_url=callback_url  # Pass the correct one
        )

        if paystack_response.get("status"):
            return Response({"payment_url": paystack_response["data"]["authorization_url"]})
        else:
            return Response({"error": "Failed to initialize payment."}, status=400)


# Manual verification view
class VerifyEventPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"error": "Reference is required"}, status=400)

        # Verify via Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        res = requests.get(url, headers=headers).json()

        if not res.get("status") or res["data"]["status"] != "success":
            return Response({"error": "Payment not verified"}, status=400)

        metadata = res["data"].get("metadata", {})
        event_id = metadata.get("event_id")
        user_id = metadata.get("user_id")

        if not event_id or not user_id:
            return Response({"error": "Incomplete payment metadata"}, status=400)

        event = get_object_or_404(Event, id=event_id, organizer=request.user)

        # Check if already paid
        if event.is_paid:
            return Response({"message": "Event already published."}, status=200)

        event.is_paid = True
        event.is_published = True
        event.save()

        return Response({"message": "Payment verified and event published."})



class PublishedEventListView(generics.ListAPIView):
    queryset = Event.objects.filter(is_published=True).order_by('start_date')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class OrganizerEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user).order_by('-created_at')
    
class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.filter(is_published=True)
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'  # 🧠 This makes /detail/<slug>/ work!

# Ticket booking
class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TicketBookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = request.user
        event_id = serializer.validated_data['event_id']
        quantity = serializer.validated_data['quantity']

        event = get_object_or_404(Event, id=event_id, is_published=True)

        if event.tickets_sold + quantity > event.capacity:
            return Response({"error": "Not enough tickets available"}, status=400)

        # ✅ Ensure organizer has a connected payout account
        if not event.organizer.subaccount_code:
            return Response({
                "error": "Organizer has not connected payout account. Please contact the organizer."
            }, status=400)

        amount = event.ticket_price * quantity
        subaccount = event.organizer.subaccount_code

        # ✅ Define callback URL *inside* the method
        callback_url = f"{settings.FRONTEND_BASE_URL}/payment-ticket-success"

        metadata = {
            "event_id": event.id,
            "user_id": user.id,
            "quantity": quantity,
            "type": "ticket_purchase"
        }

        paystack_response = initialize_paystack_transaction(
            email=user.email,
            amount=amount,
            metadata=metadata,
            subaccount=subaccount,
            callback_url=callback_url
        )

        if paystack_response.get("status"):
            Transaction.objects.create(
                user=user,
                reference=paystack_response["data"]["reference"],
                amount=amount,
                transaction_type="ticket_purchase"
            )

            return Response({
                "payment_url": paystack_response["data"]["authorization_url"],
                "reference": paystack_response["data"]["reference"]
            })

        return Response({"error": "Failed to initiate payment"}, status=400)


class VerifyTicketPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get('reference')
        user = request.user

        if not reference:
            return Response({"error": "Reference required"}, status=400)

        # Paystack verification
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        res = requests.get(url, headers=headers).json()
        if not res.get("status"):
            return Response({"error": "Invalid reference"}, status=400)

        pay_data = res["data"]
        if pay_data["status"] != "success":
            return Response({"error": "Payment not successful"}, status=400)

        # Extract meta
        meta = pay_data.get("metadata", {})
        event_id = meta.get("event_id")
        quantity = int(meta.get("quantity", 1))

        event = get_object_or_404(Event, id=event_id)

        if event.tickets_sold + quantity > event.capacity:
            return Response({"error": "Event full"}, status=400)

        # Prevent duplicate ticket
        ticket, created = Ticket.objects.get_or_create(
            reference=reference,
            defaults={
                'user': user,
                'event': event,
                'quantity': quantity,
            }
        )

        if created:
            event.tickets_sold += quantity
            event.save()
            Transaction.objects.filter(reference=reference).update(verified=True)

        # ✅ Serialize ticket details
        serializer = TicketConfirmationSerializer(ticket, context={'request': request})
        return Response(serializer.data)


def send_ticket_email(user, ticket, request):
    subject = f"🎟️ Your Ticket for {ticket.event.title}"

    # Render HTML content from a template
    html_content = render_to_string("emails/ticket_email.html", {
        "user": user,
        "ticket": ticket,
        "event": ticket.event,
        "qr_url": request.build_absolute_uri(ticket.qr_code.url) if ticket.qr_code else "",
    })

    # Create email with HTML support
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"

    # Attach QR code image if available
    if ticket.qr_code:
        email.attach_file(ticket.qr_code.path)

    email.send(fail_silently=True)

class MyTicketsView(generics.ListAPIView):
    serializer_class = MyTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # For QR full URL
        return context
    
class OrganizerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type != 'organizer':
            return Response({"error": "Access denied"}, status=403)

        events = Event.objects.filter(organizer=user).order_by('-created_at')
        total_events = events.count()
        total_tickets = Ticket.objects.filter(event__in=events).count()
        total_revenue = sum(event.ticket_price * event.tickets_sold for event in events)

        # Get 5 most recent events
        recent_events = [
            {
                "title": e.title,
                "tickets_sold": e.tickets_sold,
                "revenue": float(e.ticket_price * e.tickets_sold),
            }
            for e in events[:5]
        ]

        return Response({
            "total_events": total_events,
            "total_tickets": total_tickets,
            "total_revenue": float(total_revenue),
            "recent_events": recent_events  # ✅ Add this!
        })
    
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Ticket
from django.shortcuts import get_object_or_404
from .serializers import Event  # make sure you import your Event model

class TicketDetailView(APIView):
    def get(self, request, reference):
        ticket = get_object_or_404(Ticket, reference=reference)
        event = ticket.event

        return Response({
            "event_title": event.title,
            "event_location": event.location,
            "event_date": event.start_date,
            "qr_code": request.build_absolute_uri(ticket.qr_code.url) if ticket.qr_code else None,
            "quantity": ticket.quantity,
            "amount_paid": ticket.quantity * event.ticket_price,
            "reference": ticket.reference,
        })
