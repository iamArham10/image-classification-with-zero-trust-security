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
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import ClassificationInterface from '../components/ClassificationInterface';
import AdminManagement from '../components/AdminManagement';
import UserManagement from '../components/UserManagement';
import ClassificationLogs from '../components/ClassificationLogs';
import AuditLogs from '../components/AuditLogs';

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
  const [activeTab, setActiveTab] = useState(0);
  const [classificationHistory, setClassificationHistory] = useState<ClassificationHistory[]>([]);

  useEffect(() => {
    if (!isAuthenticated || userType !== 'admin') {
      navigate('/login');
      return;
    }

    // Fetch classification history
    const fetchHistory = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/classification/history', {
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
          imageUrl: `http://localhost:8000/api/v1/classification/image/${item.classification_id}`,
          result: item.top_prediction,
          confidence: item.confidence_score,
          timestamp: new Date(item.classification_timestamp).toLocaleString(),
          status: item.status
        })));
      } catch (error) {
        console.error('Error fetching history:', error);
      }
    };

    fetchHistory();
  }, [isAuthenticated, userType, navigate, token]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleClassify = async (image: File) => {
    try {
      const formData = new FormData();
      formData.append('file', image);

      const response = await fetch('http://localhost:8000/api/v1/classification/classify', {
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
        imageUrl: `http://localhost:8000/api/v1/classification/image/${result.classification_id}`,
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
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Admin Dashboard
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
        <Tabs value={activeTab} onChange={handleTabChange} centered>
          <Tab label="Manage Admins" />
          <Tab label="Manage Users" />
          <Tab label="Audit Logs" />
          <Tab label="Classification" />
          <Tab label="Classification Logs" />
        </Tabs>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
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
      </Container>
    </Box>
  );
};

export default AdminDashboard; 