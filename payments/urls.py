from .views import MyTransactionsView
from django.urls import path

urlpatterns = [
    path('history/', MyTransactionsView.as_view(), name='my-transactions'),
]
