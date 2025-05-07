export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'driver' | 'rider';
  phone_number?: string;
  is_active: boolean;
}

export interface RideStats {
  totalRides: number;
  activeRides: number;
  completedRides: number;
  cancelledRides: number;
}

export interface Ride {
  id: number;
  passenger: User;
  driver: User;
  pickup_location: string;
  dropoff_location: string;
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
} 