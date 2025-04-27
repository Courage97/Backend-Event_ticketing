from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import VendorService, VendorBooking, EventVendorRequest
from .serializers import (
    VendorServiceSerializer,
    VendorBookingSerializer,
    MyVendorBookingSerializer,
    EventVendorRequestSerializer,
)


# 🔍 List all active vendor services
class VendorServiceListView(generics.ListAPIView):
    queryset = VendorService.objects.filter(is_active=True)
    serializer_class = VendorServiceSerializer


# 🔎 View details of a vendor service by slug
class VendorServiceDetailView(RetrieveAPIView):
    queryset = VendorService.objects.filter(is_active=True)
    serializer_class = VendorServiceSerializer
    lookup_field = 'slug'


# ➕ Create a new vendor service (vendor only)
class VendorServiceCreateView(generics.CreateAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user, is_active=True)
        


# 📆 Create a vendor booking
class VendorBookingCreateView(generics.CreateAPIView):
    serializer_class = VendorBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 📋 Get all bookings made by the logged-in user
class MyVendorBookingsView(generics.ListAPIView):
    serializer_class = MyVendorBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VendorBooking.objects.filter(user=self.request.user).order_by('-created_at')


# 📤 Organizer sends vendor request for an event
class EventVendorRequestCreateView(generics.CreateAPIView):
    queryset = EventVendorRequest.objects.all()
    serializer_class = EventVendorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


# 📥 Vendor views incoming requests
class MyVendorRequestsView(generics.ListAPIView):
    serializer_class = EventVendorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventVendorRequest.objects.filter(vendor_service__vendor=self.request.user)


# 🔁 Vendor responds to a specific request via slug
class RespondToVendorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        action = request.data.get("action")
        if action not in ['accepted', 'declined']:
            return Response({"error": "Invalid action"}, status=400)

        vendor_request = get_object_or_404(
            EventVendorRequest,
            vendor_service__slug=slug,
            vendor_service__vendor=request.user
        )

        vendor_request.status = action
        vendor_request.save()
        return Response({"message": f"Request {action}."})


# 📬 Organizer views requests they sent
class MySentVendorRequestsView(generics.ListAPIView):
    serializer_class = EventVendorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventVendorRequest.objects.filter(organizer=self.request.user)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EventVendorRequest

from .models import VendorBooking

class VendorDashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != 'vendor':
            return Response({"error": "Access denied"}, status=403)

        # Vendor requests from organizers
        vendor_requests = EventVendorRequest.objects.filter(vendor_service__vendor=user)
        total_requests = vendor_requests.count()
        total_accepted = vendor_requests.filter(status='accepted').count()
        total_declined = vendor_requests.filter(status='declined').count()

        recent_requests = vendor_requests.order_by('-created_at')[:5]
        recent_requests_data = [
            {
                "event_title": r.event.title,
                "organizer_name": r.organizer.username,
                "status": r.status,
                "created_at": r.created_at
            }
            for r in recent_requests
        ]

        # Vendor bookings (from guests or organizers)
        bookings = VendorBooking.objects.filter(service__vendor=user)
        total_bookings = bookings.count()
        confirmed_bookings = bookings.filter(status='confirmed').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()

        recent_bookings = bookings.order_by('-created_at')[:5]
        recent_bookings_data = [
            {
                "user": b.user.username,
                "service": b.service.service_name,
                "date": b.date,
                "time": b.time,
                "status": b.status
            }
            for b in recent_bookings
        ]

        return Response({
            "total_requests": total_requests,
            "total_accepted_requests": total_accepted,
            "total_declined_requests": total_declined,
            "recent_requests": recent_requests_data,

            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "recent_bookings": recent_bookings_data
        })

