from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Hotel, Booking, RoomType

class BookingHoldTests(TestCase):
    def setUp(self):
        # create test data
        self.hotel = Hotel.objects.create(name='Test Hotel', address='123 Test St', star_rating=3)
        self.room_type = RoomType.objects.create(type_name='Deluxe Room', price=100, availability=5, hotel=self.hotel)
    
    def test_booking_hold(self):
        response = self.client.post(reverse('hold_booking', args=[self.hotel.id]), {
            f'room_quantity_{self.room_type.id}': 2
        })
        self.assertEqual(response.status_code, 200)
        
        # verify that the booking is created and held for two days
        booking = Booking.objects.get(hotel=self.hotel)
        self.assertEqual(booking.status, 'ONHOLD')
        self.assertEqual(booking.expiration_date, timezone.now() + timedelta(days=2))

    def test_email_notification(self):
        response = self.client.post(reverse('hold_booking', args=[self.hotel.id]), {
            f'room_quantity_{self.room_type.id}': 2
        })
        
        # verify that the email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Booking Hold Confirmation', mail.outbox[0].subject)


