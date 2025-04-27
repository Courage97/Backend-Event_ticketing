from django.urls import path
from .views import (
    VendorServiceListView,
    VendorServiceDetailView,
    VendorServiceCreateView,
    VendorBookingCreateView,
    MyVendorBookingsView,
    EventVendorRequestCreateView,
    MyVendorRequestsView,
    RespondToVendorRequestView,
    MySentVendorRequestsView,
    VendorDashboardSummaryView

)

urlpatterns = [
    path('services/', VendorServiceListView.as_view(), name='vendor-service-list'),
    path('services/create/', VendorServiceCreateView.as_view(), name='vendor-service-create'),
    path('services/<slug:slug>/', VendorServiceDetailView.as_view(), name='vendor-service-detail'),
    path('book/', VendorBookingCreateView.as_view(), name='vendor-book-service'),
    path('my-bookings/', MyVendorBookingsView.as_view(), name='my-vendor-bookings'),
    # linking event organizers to vendor
    path('request/', EventVendorRequestCreateView.as_view(), name='event-vendor-request'),
    path('my-requests/', MyVendorRequestsView.as_view(), name='vendor-my-requests'),
    path('respond-request/<slug:slug>/', RespondToVendorRequestView.as_view(), name='respond-vendor-request'),
    path('sent-requests/', MySentVendorRequestsView.as_view(), name='organizer-sent-requests'),
    path('dashboard-summary/', VendorDashboardSummaryView.as_view(), name='vendor-dashboard-summary'),

]

