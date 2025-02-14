from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from airline.models import Airplane, Flight, Reservation
from django.utils import timezone
import datetime

class AirlineAPITests(APITestCase):
    def setUp(self):
        # Create a valid airplane
        self.airplane = Airplane.objects.create(
            tail_number='TC-HZC',
            model='Airbus A320',
            capacity=2,  # Use a small capacity for edge case testing
            production_year=2015,
            status=True
        )
        # Create a valid flight for that airplane
        self.flight = Flight.objects.create(
            flight_number='123HZC',
            departure='LONDON Airport',
            destination='Istanbul Airport',
            departure_time=timezone.now() + datetime.timedelta(weeks=3),
            arrival_time=timezone.now() + datetime.timedelta(weeks=3, hours=4),
            airplane=self.airplane
        )
        # Create an initial reservation
        self.reservation = Reservation.objects.create(
            passenger_name='Hasim Zafer Cicek',
            passenger_email='hasimcicek@cpaths.org',
            flight=self.flight,
            status=True
        )

    # ---------- Airplane Endpoint Tests ----------
    def test_list_airplanes(self):
        url = reverse('airplane-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_airplane_details_valid(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tail_number'], self.airplane.tail_number)

    def test_get_airplane_details_invalid(self):
        url = reverse('airplane-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_airplane_valid(self):
        url = reverse('airplane-list')
        data = {
            'tail_number': 'TC-XYZ',
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': 2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tail_number'], data['tail_number'])

    def test_add_airplane_invalid_data(self):
        url = reverse('airplane-list')
        # Missing required field: tail_number
        data = {
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': 2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])

    def test_add_airplane_invalid_capacity(self):
        url = reverse('airplane-list')
        # Capacity must be a positive integer
        data = {
            'tail_number': 'TC-XYZ',
            'model': 'Boeing 737',
            'capacity': -10,
            'production_year': 2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_airplane_minus_production_year(self):
        url = reverse('airplane-list')
        # Production year must be a positive integer
        data = {
            'tail_number': 'TC-XYZ',
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': -2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_airplane_future_production_year(self):
        url = reverse('airplane-list')
        # Production year must not be in the future
        data = {
            'tail_number': 'TC-XYZ',
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': 2026,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_airplane_invalid_status(self):
        url = reverse('airplane-list')
        # Status must be a boolean
        data = {
            'tail_number': self.airplane.tail_number,
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': 2018,
            'status': 'True'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_airplane_nonunique_tail_number(self):
        url = reverse('airplane-list')
        # Tail number must be unique
        data = {
            'tail_number': self.airplane.tail_number,
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': 2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_add_airplane_long_tail_number(self):
        url = reverse('airplane-list')
        # Tail number can have a maximum of 20 characters
        data = {
            'tail_number': 'TC-12345678901234567890',
            'model': 'Boeing 737',
            'capacity': 160,
            'production_year': 2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_airplane_long_model(self):
        url = reverse('airplane-list')
        # Model can have a maximum of 50 characters
        data = {
            'tail_number': 'TC-XYZ',
            'model': 'Boeing 737 123456789012345678901234567890123456789012345678901234567890',
            'capacity': 160,
            'production_year': 2018,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_airplane(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'status': False}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airplane.refresh_from_db()
        self.assertEqual(self.airplane.status, False)
    
    def test_update_airplane_invalid_capacity(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'capacity': -10}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_airplane_invalid_production_year(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'production_year': -2018}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_airplane_future_production_year(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'production_year': 2026}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_airplane_invalid_status(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'status': 15}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_airplane_nonunique_tail_number(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'tail_number': self.airplane.tail_number}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_airplane_long_tail_number(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'tail_number': 'TC-12345678901234567890'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_airplane_long_model(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        data = {'model': 'Boeing 737 123456789012345678901234567890123456789012345678901234567890'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_airplane(self):
        url = reverse('airplane-detail', args=[self.airplane.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Ensure it is deleted
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------- Flight Endpoint Tests ----------
    def test_list_flights(self):
        url = reverse('flight-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_flight_details_valid(self):
        url = reverse('flight-detail', args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['flight_number'], self.flight.flight_number)

    def test_get_flight_details_invalid(self):
        url = reverse('flight-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_flight_valid(self):
        url = reverse('flight-list')
        data = {
            'flight_number': 'TK456',
            'departure': 'Istanbul Airport',
            'destination': 'Manchester Airport',
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() + datetime.timedelta(weeks=4,hours=4),
            'airplane': self.airplane.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['flight_number'], data['flight_number'])

    def test_add_flight_invalid_missing_fields(self):
        url = reverse('flight-list')
        data = {
            # Missing flight_number and times.
            'departure': 'Istanbul Airport',
            'destination': 'Heathrow Airport',
            'airplane': self.airplane.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_flight_invalid_times(self):
        url = reverse('flight-list')
        data = {
            'flight_number': 'TK456',
            'departure': 'Istanbul Airport',
            'destination': 'Manchester Airport',
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() - datetime.timedelta(weeks=4),
            'airplane': self.airplane.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_flight_invalid_airplane(self):
        url = reverse('flight-list')
        data = {
            'flight_number': 'TK456',
            'departure': 'Istanbul Airport',
            'destination': 'Manchester Airport',
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() + datetime.timedelta(weeks=4,hours=4),
            'airplane': 9999
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_flight_invalid_departure(self):
        url = reverse('flight-list')
        # Departure can have a maximum of 100 characters
        data = {
            'flight_number': 'TK456',
            'departure': 'Istanbul Airport 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
            'destination': 'Manchester Airport',
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() + datetime.timedelta(weeks=4,hours=4),
            'airplane': self.airplane.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_flight_invalid_destination(self):
        url = reverse('flight-list')
        # Destination can have a maximum of 100 characters
        data = {
            'flight_number': 'TK456',
            'departure': 'Istanbul Airport',
            'destination': 'Manchester Airport 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() + datetime.timedelta(weeks=4,hours=4),
            'airplane': self.airplane.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_flight_invalid_flight_number(self):
        url = reverse('flight-list')
        # Flight number can have a maximum of 20 characters
        data = {
            'flight_number': 'TK456 12345678901234567890',
            'departure': 'Istanbul Airport',
            'destination': 'Manchester Airport',
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() + datetime.timedelta(weeks=4,hours=4),
            'airplane': self.airplane.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_flight(self):
        url = reverse('flight-detail', args=[self.flight.id])
        data = {'destination': 'New Destination'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.destination, 'New Destination')

    def test_update_flight_invalid_times(self):
        url = reverse('flight-detail', args=[self.flight.id])
        data = {
            'departure_time': timezone.now() + datetime.timedelta(weeks=4),
            'arrival_time': timezone.now() - datetime.timedelta(weeks=4),
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_flight_invalid_airplane(self):
        url = reverse('flight-detail', args=[self.flight.id])
        data = {'airplane': 9999}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_flight_invalid_departure(self):
        url = reverse('flight-detail', args=[self.flight.id])
        # Departure can have a maximum of 100 characters
        data = {'departure': 'Istanbul Airport 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_flight_invalid_destination(self):
        url = reverse('flight-detail', args=[self.flight.id])
        # Destination can have a maximum of 100 characters
        data = {'destination': 'Manchester Airport 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_flight_invalid_flight_number(self):
        url = reverse('flight-detail', args=[self.flight.id])
        # Flight number can have a maximum of 20 characters
        data = {'flight_number': 'TK456 12345678901234567890'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_flight(self):
        url = reverse('flight-detail', args=[self.flight.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_flight_reservations_action(self):
        # Ensure the custom action for flight reservations works
        url = reverse('flight-reservations', args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that at least one reservation is returned
        self.assertGreaterEqual(len(response.data), 1)

    # ---------- Reservation Endpoint Tests ----------
    def test_list_reservations(self):
        url = reverse('reservation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_reservation_details_valid(self):
        url = reverse('reservation-detail', args=[self.reservation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['passenger_name'], self.reservation.passenger_name)

    def test_get_reservation_details_invalid(self):
        url = reverse('reservation-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_reservation_valid(self):
        url = reverse('reservation-list')
        data = {
            'passenger_name': 'Jane Doe',
            'passenger_email': 'jane@example.com',
            'flight': self.flight.id,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('reservation_code', response.data)

    def test_add_reservation_flight_full(self):
        # Create reservations to fill the flight capacity (capacity == 2)
        Reservation.objects.create(
            passenger_name='Passenger 2',
            passenger_email='p2@example.com',
            flight=self.flight,
            status=True
        )
        url = reverse('reservation-list')
        data = {
            'passenger_name': 'Late Comer',
            'passenger_email': 'late@example.com',
            'flight': self.flight.id,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        # Expect a 400 response as the flight is full
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_reservation_invalid_data(self):
        url = reverse('reservation-list')
        # Missing required field: passenger_name
        data = {
            'passenger_email': 'hasimcicek@cpaths.org',
            'flight': self.flight.id,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_reservation_invalid_email(self):
        url = reverse('reservation-list')
        # Invalid email format
        data = {
            'passenger_name': 'Hasim Zafer Cicek',
            'passenger_email': 'hasimcicek',
            'flight': self.flight.id,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_reservation_invalid_status(self):
        url = reverse('reservation-list')
        # Status must be a boolean
        data = {
            'passenger_name': 'Hasim Zafer Cicek',
            'passenger_email': 'hasimcicek@cpaths.org',
            'flight': self.flight.id,
            'status': 10
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_reservation_invalid_flight(self):
        url = reverse('reservation-list')
        data = {
            'passenger_name': 'Hasim Zafer Cicek',
            'passenger_email': 'hasimcicek@cpaths.org',
            'flight': 9999,
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_reservation_nonunique_reservation_code(self):
        url = reverse('reservation-list')
        # Reservation code must be unique
        data = {
            'passenger_name': 'Hasim Zafer Cicek',
            'passenger_email': 'hasimcicek@cpaths.org',
            'flight': self.flight.id,
            'status': True,
            'reservation_code': self.reservation.reservation_code
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_reservation(self):
        url = reverse('reservation-detail', args=[self.reservation.id])
        data = {'status': False}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, False)

    def test_update_reservation_invalid_email(self):
        url = reverse('reservation-detail', args=[self.reservation.id])
        data = {'passenger_email': 'invalid-email'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_reservation_invalid_status(self):
        url = reverse('reservation-detail', args=[self.reservation.id])
        data = {'status': 10}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_reservation_invalid_flight(self):
        url = reverse('reservation-detail', args=[self.reservation.id])
        data = {'flight': 9999}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_reservation_nonunique_reservation_code(self):
        url = reverse('reservation-detail', args=[self.reservation.id])
        # Reservation code must be unique
        data = {'reservation_code': self.reservation.reservation_code}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_reservation_full_flight(self):
        # Create reservations to fill the flight capacity (capacity == 2)
        Reservation.objects.create(
            passenger_name='Passenger 2',
            passenger_email='hasimcicek@cpaths.org',
            flight=self.flight,
            status=True
        )
        url = reverse('reservation-detail', args=[self.reservation.id])
        data = {'flight': self.flight.id}
        response = self.client.patch(url, data, format='json')
        # Expect a 400 response as the flight is full
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_reservations_by_flight(self):
        # Get reservations using the query parameter "flight_id"
        url = reverse('reservation-list') + f'?flight_id={self.flight.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure that all returned reservations belong to the specified flight.
        for res in response.data:
            self.assertEqual(res['flight'], self.flight.id)