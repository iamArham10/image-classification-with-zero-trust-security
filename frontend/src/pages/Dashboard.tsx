import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Paper,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { isAuthenticated, logout, token, userType } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
  }, [isAuthenticated, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!userType) {
    return <div>Loading...</div>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Student Attendance System
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" className="mb-4">
            Image Classification System
          </Typography>
          
          {userType === 'admin' ? (
            <>
              <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>
                Admin Dashboard
              </Typography>
              <Typography variant="body1">
                Welcome to the admin dashboard. Here you can manage users, view classification reports, and configure system settings.
              </Typography>
              {/* Add admin-specific components here */}
            </>
          ) : (
            <>
              <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>
                User Dashboard
              </Typography>
              <Typography variant="body1">
                Welcome to your dashboard. Here you can view your classification records and other personal information.
              </Typography>
              {/* Add user-specific components here */}
            </>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default Dashboard; 