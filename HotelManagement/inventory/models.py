from django.db import models
from django.contrib.auth.models import User

class Hotel(models.Model):
    hotel_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    star_rating = models.IntegerField()
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    business_registration_number = models.CharField(max_length=100)
    website_url = models.URLField(null=True, blank=True)
    room_types = models.ManyToManyField('RoomType', related_name='hotels')

    def __str__(self):
        return self.name

class RoomType(models.Model):
    room_type_id = models.CharField(max_length=100, unique=True)
    type_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.IntegerField()
    meal_plan = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.type_name
    

class Booking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('ONHOLD', 'On Hold'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')])
    creation_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    rooms = models.ManyToManyField(RoomType, through='BookingRoom')

    def __str__(self):
        return f"Booking {self.id} for {self.hotel.name}"

class BookingRoom(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} {self.room_type.type_name} in booking {self.booking.id}"
