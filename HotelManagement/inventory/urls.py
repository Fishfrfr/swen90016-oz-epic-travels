from django.urls import path
from . import views

urlpatterns = [
    path('import/', views.import_inventory, name='import_inventory'),
    path('hotels/', views.list_hotels, name='list_hotels'),
    path('book/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('hold/<int:hotel_id>/', views.hold_booking, name='hold_booking'),
]