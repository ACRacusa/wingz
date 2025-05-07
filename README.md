# Wingz Ride Management API

A Django REST Framework API for managing ride information with optimized performance and efficient query handling.

## Features

- RESTful API endpoints for managing rides
- Admin-only access control
- Efficient query optimization for large datasets
- Support for filtering and sorting
- Pagination support
- Optimized retrieval of today's ride events

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## API Usage Examples

### Authentication
First, you need to authenticate to get a token:
```bash
# Login to get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'

# Response:
{
    "token": "your_auth_token_here"
}

# Use the token in subsequent requests
curl -X GET http://localhost:8000/api/rides/ \
  -H "Authorization: Token your_auth_token_here"
```

### List Rides with Pagination
```bash
# Get first page of rides
curl -X GET "http://localhost:8000/api/rides/?page=1" \
  -H "Authorization: Token your_auth_token_here"

# Response example:
{
    "count": 100,
    "next": "http://localhost:8000/api/rides/?page=2",
    "previous": null,
    "results": [
        {
            "id_ride": 1,
            "status": "en-route",
            "rider": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone_number": "+1234567890",
                "role": "rider"
            },
            "driver": {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "phone_number": "+0987654321",
                "role": "driver"
            },
            "pickup_latitude": 37.7749,
            "pickup_longitude": -122.4194,
            "dropoff_latitude": 37.7833,
            "dropoff_longitude": -122.4167,
            "pickup_time": "2024-05-04T10:00:00Z",
            "todays_ride_events": [
                {
                    "id_ride_event": 1,
                    "description": "Status changed to en-route",
                    "created_at": "2024-05-04T09:55:00Z"
                }
            ],
            "distance_to_pickup": 2.5
        }
    ]
}
```

### Filtering Rides
```bash
# Filter by status
curl -X GET "http://localhost:8000/api/rides/?status=en-route" \
  -H "Authorization: Token your_auth_token_here"

# Filter by rider email
curl -X GET "http://localhost:8000/api/rides/?rider__email=john@example.com" \
  -H "Authorization: Token your_auth_token_here"

# Combine filters
curl -X GET "http://localhost:8000/api/rides/?status=en-route&rider__email=john@example.com" \
  -H "Authorization: Token your_auth_token_here"
```

### Sorting Rides
```bash
# Sort by pickup time (ascending)
curl -X GET "http://localhost:8000/api/rides/?ordering=pickup_time" \
  -H "Authorization: Token your_auth_token_here"

# Sort by pickup time (descending)
curl -X GET "http://localhost:8000/api/rides/?ordering=-pickup_time" \
  -H "Authorization: Token your_auth_token_here"

# Sort by distance to pickup (requires latitude and longitude)
curl -X GET "http://localhost:8000/api/rides/?ordering=distance_to_pickup&latitude=37.7749&longitude=-122.4194" \
  -H "Authorization: Token your_auth_token_here"
```

### Creating a New Ride
```bash
curl -X POST "http://localhost:8000/api/rides/" \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": 1,           # Required: ID of an existing rider user
    "driver_id": 2,          # Optional: ID of an existing driver user
    "pickup_latitude": 37.7749,
    "pickup_longitude": -122.4194,
    "dropoff_latitude": 37.7833,
    "dropoff_longitude": -122.4167,
    "pickup_time": "2024-05-04T10:00:00Z"
  }'
```

### Managing Ride Events
```bash
# List events for a specific ride
curl -X GET "http://localhost:8000/api/rides/5/events/" \
  -H "Authorization: Token your_auth_token_here"

# Create a new event for a ride
curl -X POST "http://localhost:8000/api/rides/5/events/" \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Status changed to en-route"
  }'

# Response example:
{
    "id_ride_event": 1,
    "description": "Status changed to en-route",
    "created_at": "2024-05-07T16:03:53Z"
}
```

### Updating a Ride
```bash
curl -X PUT "http://localhost:8000/api/rides/1/" \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "pickup_latitude": 37.7749,
    "pickup_longitude": -122.4194,
    "dropoff_latitude": 37.7833,
    "dropoff_longitude": -122.4167,
    "pickup_time": "2024-05-04T10:00:00Z"
  }'
```

### Deleting a Ride
```bash
curl -X DELETE "http://localhost:8000/api/rides/1/" \
  -H "Authorization: Token your_auth_token_here"
```

## Performance Optimizations

1. **Efficient Query Handling**:
   - Uses `select_related` for foreign key relationships
   - Implements `prefetch_related` for today's ride events
   - Optimizes distance calculations using raw SQL

2. **Minimal Database Queries**:
   - Achieves ride list retrieval with related data in 2-3 queries
   - Implements efficient filtering and sorting
   - Uses Django's built-in pagination

3. **Ride Events Optimization**:
   - Only retrieves events from the last 24 hours
   - Uses Prefetch objects to minimize database hits
   - Implements efficient serialization

## SQL Report Query

Here's a SQL query that analyzes ride durations by driver and month:

```sql
WITH ride_durations AS (
    SELECT 
        r.id_ride,
        r.driver_id,
        u.first_name || ' ' || u.last_name AS driver_name,
        DATE_TRUNC('month', r.pickup_time) AS month,
        -- Calculate duration between pickup and dropoff events
        MAX(CASE WHEN re.description = 'Status changed to dropoff' THEN re.created_at END) -
        MAX(CASE WHEN re.description = 'Status changed to pickup' THEN re.created_at END) AS duration
    FROM rides_ride r
    JOIN rides_rideevent re ON r.id_ride = re.ride_id
    JOIN rides_user u ON r.driver_id = u.id
    WHERE re.description IN ('Status changed to pickup', 'Status changed to dropoff')
    GROUP BY r.id_ride, r.driver_id, u.first_name, u.last_name, DATE_TRUNC('month', r.pickup_time)
)
SELECT 
    TO_CHAR(month, 'YYYY-MM') AS month,
    driver_name AS driver,
    COUNT(*) AS "Count of Trips > 1 hr",
    AVG(EXTRACT(EPOCH FROM duration)/3600)::numeric(10,2) AS "Avg Duration (hours)"
FROM ride_durations
WHERE duration > INTERVAL '1 hour'
GROUP BY month, driver_name
ORDER BY month, driver_name;
```