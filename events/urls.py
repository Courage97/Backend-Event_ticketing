from django.urls import path
from .views import (
    EventCreateView,
    InitiateEventPaymentView,
    VerifyEventPaymentView,
    PublishedEventListView,
    OrganizerEventListView,
    EventDetailView,
    BookTicketView,
    VerifyTicketPaymentView,
    MyTicketsView,
    OrganizerDashboardView,
    TicketDetailView
)

urlpatterns = [
    path('create/', EventCreateView.as_view(), name='event-create'),
    path('initiate-payment/', InitiateEventPaymentView.as_view(), name='initiate-event-payment'),
    path('verify-payment/', VerifyEventPaymentView.as_view(), name='verify-event-payment'),
    path('list/', PublishedEventListView.as_view(), name='published-events'),
    path('my-events/', OrganizerEventListView.as_view(), name='organizer-events'),
    path('detail/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('book-ticket/', BookTicketView.as_view(), name='book-ticket'),
    path('verify-ticket-payment/', VerifyTicketPaymentView.as_view(), name='verify-ticket'),
    path('my-tickets/', MyTicketsView.as_view(), name='my-tickets'),
    path('dashboard/summary/', OrganizerDashboardView.as_view(), name='organizer-dashboard'),
    path('ticket/<str:reference>/', TicketDetailView.as_view(), name='ticket-detail'),

]
