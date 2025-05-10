import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Tabs,
  Tab,
  Avatar,
  IconButton,
  Paper,
  Divider,
  useTheme,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import ClassificationInterface from '../components/ClassificationInterface';
import AdminManagement from '../components/AdminManagement';
import UserManagement from '../components/UserManagement';
import ClassificationLogs from '../components/ClassificationLogs';
import AuditLogs from '../components/AuditLogs';
import MenuIcon from '@mui/icons-material/Menu';
import LogoutIcon from '@mui/icons-material/Logout';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PeopleIcon from '@mui/icons-material/People';
import HistoryIcon from '@mui/icons-material/History';
import ImageSearchIcon from '@mui/icons-material/ImageSearch';
import AssessmentIcon from '@mui/icons-material/Assessment';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

interface ClassificationHistory {
  id: string;
  imageUrl: string;
  result: string;
  confidence: number;
  timestamp: string;
  status: string;
}

const AdminDashboard = () => {
  const { isAuthenticated, logout, userType, token } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [classificationHistory, setClassificationHistory] = useState<ClassificationHistory[]>([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [username, setUsername] = useState('Admin User');

  useEffect(() => {
    if (!isAuthenticated || userType !== 'admin') {
      navigate('/login');
      return;
    }

    // Fetch user profile
    const fetchUserProfile = async () => {
      try {
        const response = await fetch('https://localhost:8000/api/v1/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUsername(userData.username || 'Admin User');
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
            'Authorization': `Bearer ${token}`,
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
  }, [isAuthenticated, userType, navigate, token]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleTabChange = (newValue: number) => {
    setActiveTab(newValue);
    setDrawerOpen(false);
  };

  const handleClassify = async (image: File) => {
    try {
      const formData = new FormData();
      formData.append('file', image);

      const response = await fetch('https://localhost:8000/api/v1/classification/classify', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Classification failed');
      }

      const result = await response.json();
      
      // Add to history
      const newHistoryItem: ClassificationHistory = {
        id: result.classification_id.toString(),
        imageUrl: `https://localhost:8000/api/v1/classification/image/${result.classification_id}`,
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

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const drawerItems = [
    { text: 'Manage Admins', icon: <AdminPanelSettingsIcon />, index: 0 },
    { text: 'Manage Users', icon: <PeopleIcon />, index: 1 },
    { text: 'Audit Logs', icon: <HistoryIcon />, index: 2 },
    { text: 'Classification', icon: <ImageSearchIcon />, index: 3 },
    { text: 'Classification Logs', icon: <AssessmentIcon />, index: 4 },
  ];

  const drawer = (
    <Box sx={{ width: 250 }} role="presentation">
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Avatar 
          sx={{ 
            width: 80, 
            height: 80, 
            mb: 1,
            bgcolor: theme.palette.primary.main
          }}
        >
          <AccountCircleIcon sx={{ fontSize: 50 }} />
        </Avatar>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600 }}>
          {username}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Administrator
        </Typography>
      </Box>
      <Divider />
      <List>
        {drawerItems.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            onClick={() => handleTabChange(item.index)}
            selected={activeTab === item.index}
            sx={{
              '&.Mui-selected': {
                backgroundColor: `${theme.palette.primary.light}20`,
                borderLeft: `4px solid ${theme.palette.primary.main}`,
                '& .MuiListItemIcon-root': {
                  color: theme.palette.primary.main
                },
                '& .MuiListItemText-primary': {
                  fontWeight: 600,
                  color: theme.palette.primary.main
                }
              },
              '&:hover': {
                backgroundColor: `${theme.palette.primary.light}10`,
              }
            }}
          >
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem button onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon color="error" />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </Box>
  );

  const tabTitles = [
    "Admin Management",
    "User Management",
    "Audit Logs",
    "Image Classification",
    "Classification Logs"
  ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f7fa' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Admin Dashboard
          </Typography>
          <Tooltip title="Logout">
            <IconButton color="inherit" onClick={handleLogout}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={toggleDrawer}
        sx={{
          '& .MuiDrawer-paper': { boxSizing: 'border-box' },
        }}
      >
        {drawer}
      </Drawer>

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
            {tabTitles[activeTab]}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {activeTab === 0 && "Manage administrator accounts and permissions"}
            {activeTab === 1 && "Manage user accounts and access controls"}
            {activeTab === 2 && "View system audit logs and security events"}
            {activeTab === 3 && "Classify images using the trained model"}
            {activeTab === 4 && "View history of all image classifications"}
          </Typography>
        </Paper>

        <Box sx={{ mt: 2 }}>
          {activeTab === 0 && <AdminManagement token={token || ''} />}
          {activeTab === 1 && <UserManagement token={token || ''} />}
          {activeTab === 2 && <AuditLogs token={token || ''} />}
          {activeTab === 3 && (
            <ClassificationInterface
              onClassify={handleClassify}
              history={classificationHistory}
              onHistoryItemClick={handleHistoryItemClick}
            />
          )}
          {activeTab === 4 && <ClassificationLogs token={token || ''} />}
        </Box>
      </Box>
    </Box>
  );
};

export default AdminDashboard;