from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from .models import Hotel, RoomType, Booking
from .forms import CSVUploadForm
import csv
import io



# Define the Mapping Dictionary
CSV_FIELD_MAPPING = {
    'hotel': {
        'hotel_id': 'hotel_id',
        'name': 'hotel_name',
        'address': 'address',
        'star_rating': 'star_rating',
        'contact_name': 'contact_name',
        'contact_email': 'contact_email',
        'contact_phone': 'contact_phone',
        'business_registration_number': 'business_registration_number',
        'website_url': 'website_url'
    },
    'room_type': {
        'room_type_id': 'room_type_id',
        'type_name': 'room_type_name',
        'price': 'price',
        'availability': 'availability',
        'meal_plan': 'meal_plan'
    }
}

def import_inventory(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            reader = csv.DictReader(io_string)
            required_fields = set(val for dic in CSV_FIELD_MAPPING.values() for val in dic.values())

            # Check if all required fields exist in the CSV file
            if not required_fields.issubset(set(reader.fieldnames)):
                missing_fields = required_fields - set(reader.fieldnames)
                messages.error(request, f'Missing required fields: {", ".join(missing_fields)}')
                return render(request, 'inventory/import.html', {'form': form})

            for row in reader:
                hotel_data = {}
                room_data = {}

                # Map CSV fields to model fields using CSV_FIELD_MAPPING
                for model_field, csv_field in CSV_FIELD_MAPPING['hotel'].items():
                    hotel_data[model_field] = row.get(csv_field)
                for model_field, csv_field in CSV_FIELD_MAPPING['room_type'].items():
                    room_data[model_field] = row.get(csv_field)

                # Convert specific fields to the correct type
                hotel_data['star_rating'] = int(hotel_data.get('star_rating') or 0)
                room_data['price'] = float(room_data.get('price') or 0.0)
                room_data['availability'] = int(room_data.get('availability') or 0)

                # create or update the hotel and room types
                hotel, created = Hotel.objects.get_or_create(
                    hotel_id=hotel_data['hotel_id'],
                    defaults=hotel_data
                )

                room_type, created = RoomType.objects.get_or_create(
                    room_type_id=room_data['room_type_id'],
                    defaults=room_data
                )

                hotel.room_types.add(room_type)

            messages.success(request, 'CSV file has been successfully uploaded and processed.')
            return redirect('success_url')  # Redirect to a success URL

    else:
        form = CSVUploadForm()
    return render(request, 'inventory/import.html', {'form': form})

# User Story: 05
# Handle List/Search/Filter for Hotels
def list_hotels(request):
    hotels = Hotel.objects.all()
    
    # Optional Filtering
    city = request.GET.get('city')
    if city:
        hotels = hotels.filter(address__icontains=city)

    star_rating = request.GET.get('star_rating')
    if star_rating:
        hotels = hotels.filter(star_rating=star_rating)

    # Price Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price and max_price:
        hotels = hotels.filter(room_types__price__gte=min_price, room_types__price__lte=max_price)
    elif min_price:
        hotels = hotels.filter(room_types__price__gte=min_price)
    elif max_price:
        hotels = hotels.filter(room_types__price__lte=max_price)

    name = request.GET.get('name')
    if name:
        hotels = hotels.filter(name__icontains=name)
    
    hotels = hotels.distinct()

    return render(request, 'inventory/hotel_list.html', {'hotels': hotels})

# User Story: 09
# Hotel Booking
def book_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    return render(request, 'inventory/book_hotel.html', {'hotel': hotel})



# Hold booking
def hold_booking(request, hotel_id):
    
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        hotel = Hotel.objects.get(id=hotel_id)
        user = request.user  # assume the user is logged in
        booking = Booking.objects.create(
            hotel=hotel,
            user=user,
            status='ONHOLD',
            creation_date=timezone.now(),
            expiration_date=timezone.now() + timedelta(days=2)
        )

        # handle the selection for each room type
        for room_type in hotel.room_types.all():
            quantity = request.POST.get(f'room_quantity_{room_type.id}', 0)
            if quantity and int(quantity) > 0:
                booking.rooms.add(room_type, through_defaults={'quantity': int(quantity)})

        # send an email notification for the booking hold
        send_mail(
            'Booking Hold Confirmation',
            f'Your booking is on hold for 2 days at {hotel.name}.',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return render(request, 'inventory/success.html', {'message': 'Booking is on hold for 2 days.'})

    return render(request, 'inventory/book_hotel.html', {'hotel': hotel})        
