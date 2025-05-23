from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PricingPackage(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100)
    features = models.CharField(max_length=500)  # Строка с особенностями, разделёнными запятой

    def __str__(self):
        return self.name

class Client(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='client')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_client(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_client(sender, instance, **kwargs):
    instance.client.save()

class Request(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    description = models.TextField()
    pricing_package = models.ForeignKey(PricingPackage, on_delete=models.SET_NULL, null=True, blank=False)
    contact_info = models.CharField(max_length=255, verbose_name="Контактные данные", blank=True)
    event_date = models.DateField(verbose_name="Дата мероприятия", null=True, blank=True)
    guest_count = models.PositiveIntegerField(verbose_name="Количество гостей", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='new',
    )

    def __str__(self):
        return f"Request {self.id} by {self.client.user.username}"

class Testimonial(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.client.user.username}"

class ContactInfo(models.Model):
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return f"Contact Info"

class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Фото {self.id}"

from django.contrib.auth.models import User

class Review(models.Model):
    RATING_CHOICES = [(i, f'{i} звёзд') for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    text = models.TextField("Текст отзыва")
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.user.username} – {self.created_at.date()}"
