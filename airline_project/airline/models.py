# airline/models.py
from django.db import models
import string, random
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

class Airplane(models.Model):
    tail_number = models.CharField(max_length=20,unique=True) # change max_lengths if necessary I put them to use memory efficiently.
    model = models.CharField(max_length=50) 
    capacity = models.PositiveIntegerField() 
    production_year = models.PositiveIntegerField(validators=[MinValueValidator(1907), MaxValueValidator(timezone.now().year)])
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.model} ({self.tail_number})"

class Flight(models.Model):
    flight_number = models.CharField(max_length=20)
    departure = models.CharField(max_length=100) 
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    airplane = models.ForeignKey(Airplane, related_name='flights', on_delete=models.CASCADE)

    def __str__(self):
        return f"Flight {self.flight_number} from {self.departure} to {self.destination}"
    
def generate_reservation_code(length=6):
    # Generates an alphanumeric code (adjust length if necessary)
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class Reservation(models.Model):
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    reservation_code = models.CharField(max_length=10,unique=True, blank=True)
    flight = models.ForeignKey(Flight, related_name='reservations', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate reservation code if not provided
        if not self.reservation_code:
            self.reservation_code = generate_reservation_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.reservation_code} for {self.passenger_name}"
