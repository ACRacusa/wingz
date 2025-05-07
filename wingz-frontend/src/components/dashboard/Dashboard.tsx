import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import { RideStats } from '../../types';
import api from '../../services/api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<RideStats>({
    totalRides: 0,
    activeRides: 0,
    completedRides: 0,
    cancelledRides: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/rides/stats/');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
        gap: 3,
        width: '100%'
      }}>
        <div>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Rides
              </Typography>
              <Typography variant="h4" component="h2">
                {stats.totalRides}
              </Typography>
            </CardContent>
          </Card>
        </div>
        <div>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Rides
              </Typography>
              <Typography variant="h4" component="h2">
                {stats.activeRides}
              </Typography>
            </CardContent>
          </Card>
        </div>
        <div>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Completed Rides
              </Typography>
              <Typography variant="h4" component="h2">
                {stats.completedRides}
              </Typography>
            </CardContent>
          </Card>
        </div>
        <div>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Cancelled Rides
              </Typography>
              <Typography variant="h4" component="h2">
                {stats.cancelledRides}
              </Typography>
            </CardContent>
          </Card>
        </div>
      </Box>
    </Container>
  );
};

export default Dashboard; 