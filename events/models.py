from django.db import models
from django.contrib.auth import get_user_model
from .utils import generate_qr_code 
import uuid
from django.utils.text import slugify

User = get_user_model()

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    tickets_sold = models.PositiveIntegerField(default=0)

    flyer = models.ImageField(upload_to='event_flyers/', blank=True, null=True)

    is_paid = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # auto-generate slug if not provided
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Event.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)
    

# Event Ticket model
class Ticket(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    quantity = models.PositiveIntegerField(default=1)
    qr_code = models.ImageField(upload_to='tickets/', null=True, blank=True)
    reference = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid.uuid4()).replace('-', '')[:12]

        # Generate QR code only once
        if not self.qr_code:
            qr_image = generate_qr_code(f"{self.user.email}-{self.event.id}-{self.reference}")
            self.qr_code.save(f"ticket_{self.reference}.png", qr_image, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
