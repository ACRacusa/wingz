# Wingz Ride Management API

A Django REST Framework API for managing ride information with optimized performance and efficient query handling.

## Features

- RESTful API endpoints for managing rides
- Admin-only access control
- Efficient query optimization for large datasets
- Support for filtering and sorting
- Pagination support
- Distance-based sorting with GPS coordinates
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
First, you need to authenticate as an admin user:
```bash
# Using Basic Auth
curl -X GET http://localhost:8000/api/rides/ \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

# Using Session Auth (after logging in through the browser)
curl -X GET http://localhost:8000/api/rides/ \
  -H "Cookie: sessionid=your_session_id"
```

### List Rides with Pagination
```bash
# Get first page of rides
curl -X GET "http://localhost:8000/api/rides/?page=1" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

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
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

# Filter by rider email
curl -X GET "http://localhost:8000/api/rides/?rider__email=john@example.com" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

# Combine filters
curl -X GET "http://localhost:8000/api/rides/?status=en-route&rider__email=john@example.com" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"
```

### Sorting Rides
```bash
# Sort by pickup time (ascending)
curl -X GET "http://localhost:8000/api/rides/?ordering=pickup_time" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

# Sort by pickup time (descending)
curl -X GET "http://localhost:8000/api/rides/?ordering=-pickup_time" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

# Sort by distance to pickup (requires latitude and longitude)
curl -X GET "http://localhost:8000/api/rides/?ordering=distance_to_pickup&latitude=37.7749&longitude=-122.4194" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"
```

### Creating a New Ride
```bash
curl -X POST "http://localhost:8000/api/rides/" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
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

Note: When creating a new ride:
- `rider_id` is required and must reference an existing user with role='rider'
- `driver_id` is optional and must reference an existing user with role='driver' if provided
- The response will include the full rider and driver objects with all their details
- The status will default to 'pending' if not specified

### Updating a Ride
```bash
curl -X PUT "http://localhost:8000/api/rides/1/" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
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
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"
```

### Managing Ride Events
```bash
# List events for a specific ride
curl -X GET "http://localhost:8000/api/rides/5/events/" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)"

# Create a new event for a ride
curl -X POST "http://localhost:8000/api/rides/5/events/" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
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

For reporting purposes, here's the SQL query to calculate trip durations and count trips that took more than 1 hour, grouped by Month and Driver:

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

This query:
1. Creates a CTE (Common Table Expression) to calculate trip durations
2. Joins the Ride, RideEvent, and User tables
3. Uses CASE statements to find pickup and dropoff timestamps
4. Calculates the duration between these events
5. Groups results by month and driver
6. Shows:
   - Number of trips longer than 1 hour
   - Average duration of these trips
7. Orders results chronologically by month and alphabetically by driver name

## Design Decisions

1. **Custom User Model**:
   - Extended Django's AbstractUser to maintain authentication features
   - Added role-based access control
   - Maintained compatibility with Django's auth system

2. **Query Optimization**:
   - Used raw SQL for distance calculations to avoid Python-level computation
   - Implemented efficient prefetching for related data
   - Optimized filtering and sorting operations

3. **API Design**:
   - Used ViewSets for consistent CRUD operations
   - Implemented custom permissions for admin-only access
   - Added comprehensive filtering and sorting capabilities

## Challenges and Solutions

1. **Large Dataset Handling**:
   - Implemented efficient query optimization
   - Used database-level operations where possible
   - Minimized data transfer with selective field serialization

2. **Distance Calculation**:
   - Used Haversine formula in raw SQL for performance
   - Implemented caching for repeated calculations
   - Added error handling for invalid coordinates

3. **Authentication**:
   - Implemented role-based access control
   - Used Django's built-in authentication system
   - Added custom permission classes for admin access 