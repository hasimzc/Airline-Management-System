# airline/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Airplane, Flight, Reservation
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    @action(detail=True, methods=['get'])
    def flights(self):
        airplane = self.get_object()
        flights = airplane.flights.all()
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data)


# Flight ViewSet
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['departure', 'destination', 'departure_time', 'arrival_time']

    @action(detail=True, methods=['get'])
    def reservations(self, request, pk=None): 
        flight = self.get_object()
        reservations = flight.reservations.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    # Custom method to filter reservations for a specific flight
    def get_queryset(self):
        flight_id = self.request.query_params.get('flight_id')
        if flight_id:
            return Reservation.objects.filter(flight_id=flight_id)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # Call the original create() method provided by DRF
        response = super().create(request, *args, **kwargs)
        
        # Get the created reservation (assuming your serializer returns an 'id')
        reservation_id = response.data.get('id')
        if reservation_id:
            reservation = Reservation.objects.get(pk=reservation_id)
            
            # Send the confirmation email
            send_mail(
                subject='Reservation Confirmation',
                message=f'Hello {reservation.passenger_name},\n\n'
                        f'Your reservation with code {reservation.reservation_code} has been confirmed.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.passenger_email],
                fail_silently=False,  # Set to True if you don't want errors to be raised in development
            )
        
        return response

