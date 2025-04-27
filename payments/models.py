from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

TRANSACTION_TYPE = (
    ('event_publish', 'Event Publishing'),
    ('ticket_purchase', 'Ticket Purchase'),
)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reference}"
