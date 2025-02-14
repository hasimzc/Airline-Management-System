import string
import random
from rest_framework import serializers
from .models import Airplane, Flight, Reservation
from django.utils import timezone
from datetime import datetime
import pytz
# Airplane Serializer
class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = '__all__'

    def validate_tail_number(self, value):
        if Airplane.objects.filter(tail_number=value).exists():
            raise serializers.ValidationError("Tail number must be unique.")
        return value
    
    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be a positive integer greater than zero.")
        return value



# Flight Serializer
class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'
        
    def validate_arrival_time(self, value):
        # Retrieve departure_time from initial data
        arrive_time = self.initial_data.get('arrival_time')
        departure_time = self.initial_data.get('departure_time')
        # convert arrival_time and departure_time to datetime object
        arrival_time = datetime.strptime(arrive_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        departure_time = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        if arrival_time < departure_time:
            raise serializers.ValidationError("Arrival time must be after departure time.")

        return value
        
    def validate_airplane(self, value):
        # Ensure airplane is not full
        if value and Flight.objects.filter(airplane=value).count() >= value.capacity:
            raise serializers.ValidationError("This airplane is already full.")
        return value

    def validate_flight_number(self, value):
        # Ensure flight_number is unique if it's being updated.
        if Flight.objects.filter(flight_number=value).exists():
            raise serializers.ValidationError("Flight number must be unique.")
        return value
    """
    def validate_flight_number_length(self, value):
        # Ensure flight_number is less than 20 characters
        if len(value) > 20:
            raise serializers.ValidationError("Flight number must be less than 20 characters.")
        return value
    
    def validate_departure(self, value):
        # Ensure departure is less than 100 characters
        if len(value) > 100:
            raise serializers.ValidationError("Departure must be less than 100 characters.")
        return value
    
    def validate_destination(self, value):
        # Ensure destination is less than 100 characters
        if len(value) > 100:
            raise serializers.ValidationError("Destination must be less than 100 characters.")
        return value
    """
# Reservation Serializer with Custom Logic
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

    def generate_reservation_code(self):
        # Generates a random 6-character alphanumeric reservation code
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def validate(self, data):
        # Check if the flight is full before making a reservation
        flight = data.get('flight')
        if flight and Reservation.objects.filter(flight=flight).count() >= flight.airplane.capacity:
            raise serializers.ValidationError("This flight is already full.")
        return data

    def create(self, validated_data):
        # Auto-generate reservation code before saving
        validated_data['reservation_code'] = self.generate_reservation_code()
        return super().create(validated_data)
    
    def validate_reservation_code(self, value):
        # Ensure reservation_code is unique if it's being updated.
        if Reservation.objects.filter(reservation_code=value).exists():
            raise serializers.ValidationError("Reservation code must be unique.")
        return value
    
    def validate_status(self, value):
        # Ensure status is a boolean value.
        if not isinstance(value, bool):
            raise serializers.ValidationError("Status must be a boolean.")
        return value
