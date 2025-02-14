# Airline Management System

This Django-based web application streamlines the management of airplanes, flights, and reservations. Its RESTful API, built with Django REST framework, simplifies integration efforts and provides endpoints for listing, creating, updating, and deleting applicable records, along with handling reservations and email confirmations.

## Features

- **Airplane Management:** Create, update, and delete airplane details.
- **Flight Scheduling:** Easily manage flight data, including departure and arrival times with validation.
- **Reservation Handling:** Generate and view reservations, automatically create reservation codes, and send confirmation emails.
- **API Endpoints:** Leverage Django REST framework with filtering options to efficiently access and manage data.
- **Testing:** Comprehensive unit tests ensure reliable operation of core functionality.

## Getting Started

### Prerequisites
- Python 3.9 or later  
- Virtual environment (recommended)  
- [pip](https://pip.pypa.io)

## API Documentation

Below are the primary endpoints exposed by this project:

### Airplanes
- List all airplanes: `/airplanes/`
- Retrieve or update airplane details: `/airplanes/<id>/`
- List flights associated with a specific airplane: `/airplanes/<id>/flights/`

### Flights
- List all flights: `/flights/`
- Retrieve or update flight details: `/flights/<id>/`
- List reservations for a specific flight: `/flights/<id>/reservations/`

### Reservations
- List all reservations: `/reservations/`
- Retrieve or update a reservation: `/reservations/<id>/`

For implementation details, please refer to:
- `manage.py`
- Models
- Serializers
- Views

## Postman Collections
You can find example Postman collections for testing in the `postman` directory.

## Dependencies
- Django==4.2.19
- djangorestframework==3.14.0
- django-filter==23.2
- pytz

## License
This project is licensed under the MIT License. See the `LICENSE` file for additional information.

## Contact
For inquiries or further information, please reach out to:
- **Name:** Haşim Zafer ÇİÇEK
- **Email:** hasimzafer.cicek@gmail.com

Feel free to adjust any sections or details to best fit your project requirements.
