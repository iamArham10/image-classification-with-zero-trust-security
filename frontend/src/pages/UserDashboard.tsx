import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Paper,
  Avatar,
  IconButton,
  Tooltip,
  useTheme,
  Divider,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import ClassificationInterface from '../components/ClassificationInterface';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ImageSearchIcon from '@mui/icons-material/ImageSearch';

interface ClassificationHistory {
  id: string;
  imageUrl: string;
  result: string;
  confidence: number;
  timestamp: string;
  status: string;
}

const UserDashboard = () => {
  const { isAuthenticated, logout, userType, token } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const [classificationHistory, setClassificationHistory] = useState<ClassificationHistory[]>([]);
  const [username, setUsername] = useState('User');

  useEffect(() => {
    if (!isAuthenticated || userType !== 'user') {
      navigate('/login');
      return;
    }

    // Fetch user profile
    const fetchUserProfile = async () => {
      try {
        const response = await fetch('https://localhost:8000/api/v1/users/me', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUsername(userData.username || 'User');
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    };

    // Fetch classification history
    const fetchHistory = async () => {
      try {
        const response = await fetch('https://localhost:8000/api/v1/classification/history', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch history');
        }

        const history = await response.json();
        setClassificationHistory(history.map((item: any) => ({
          id: item.classification_id.toString(),
          imageUrl: `https://localhost:8000/api/v1/classification/image/${item.classification_id}`,
          result: item.top_prediction,
          confidence: item.confidence_score,
          timestamp: new Date(item.classification_timestamp).toLocaleString(),
          status: item.status
        })));
      } catch (error) {
        console.error('Error fetching history:', error);
      }
    };

    fetchUserProfile();
    fetchHistory();
  }, [isAuthenticated, userType, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleClassify = async (image: File) => {
    try {
      const formData = new FormData();
      formData.append('file', image);

      const response = await fetch('https://localhost:8000/api/v1/classification/classify', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Classification failed');
      }

      const result = await response.json();
      
      // Add to history
      const newHistoryItem: ClassificationHistory = {
        id: result.classification_id.toString(),
        imageUrl: URL.createObjectURL(image),
        result: result.top_prediction,
        confidence: result.confidence_score,
        timestamp: new Date().toLocaleString(),
        status: result.confidence_score >= 0.60 ? 'success' : 'failed'
      };
      
      setClassificationHistory(prev => [newHistoryItem, ...prev]);
      
      return {
        top_prediction: result.top_prediction,
        confidence_score: result.confidence_score
      };
    } catch (error) {
      console.error('Classification error:', error);
      throw error;
    }
  };

  const handleHistoryItemClick = (item: ClassificationHistory) => {
    // Handle history item click
    console.log('History item clicked:', item);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f7fa' }}>
      <AppBar position="fixed">
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ImageSearchIcon sx={{ mr: 1.5 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              Image Classification
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar 
              sx={{ 
                width: 32, 
                height: 32, 
                mr: 1,
                bgcolor: theme.palette.primary.main
              }}
            >
              <AccountCircleIcon fontSize="small" />
            </Avatar>
            <Typography variant="body2" sx={{ mr: 2 }}>
              {username}
            </Typography>
            <Tooltip title="Logout">
              <IconButton color="inherit" onClick={handleLogout} edge="end">
                <LogoutIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: '100%',
          mt: '64px',
        }}
      >
        <Paper 
          elevation={0} 
          sx={{ 
            p: 2, 
            mb: 3, 
            borderRadius: 2,
            backgroundColor: theme.palette.background.paper,
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
          }}
        >
          <Typography variant="h5" component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
            Image Classification
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload and classify images using our trained machine learning model
          </Typography>
        </Paper>

        <Box sx={{ mt: 2 }}>
          <ClassificationInterface
            onClassify={handleClassify}
            history={classificationHistory}
            onHistoryItemClick={handleHistoryItemClick}
          />
        </Box>
      </Box>
    </Box>
  );
};

export default UserDashboard;