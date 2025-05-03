import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  CircularProgress,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const UserDashboard = () => {
  const { isAuthenticated, logout, userType } = useAuth();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [classificationResult, setClassificationResult] = useState<any>(null);

  useEffect(() => {
    if (!isAuthenticated || userType !== 'user') {
      navigate('/login');
      return;
    }
  }, [isAuthenticated, userType, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleClassify = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await fetch('http://localhost:8000/api/v1/classify', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      setClassificationResult(result);
    } catch (error) {
      console.error('Classification error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            User Dashboard
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Image Classification
        </Typography>
        
        <Grid container spacing={3}>
          {/* Image Upload Card */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Upload Image
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Select an image to classify
                </Typography>
                <input
                  accept="image/*"
                  style={{ display: 'none' }}
                  id="raised-button-file"
                  type="file"
                  onChange={handleFileChange}
                />
                <label htmlFor="raised-button-file">
                  <Button
                    variant="contained"
                    component="span"
                    sx={{ mr: 2 }}
                  >
                    Choose File
                  </Button>
                </label>
                {selectedFile && (
                  <Typography variant="body2">
                    Selected: {selectedFile.name}
                  </Typography>
                )}
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleClassify}
                  disabled={!selectedFile || isLoading}
                  sx={{ mt: 2, display: 'block' }}
                >
                  {isLoading ? <CircularProgress size={24} /> : 'Classify Image'}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Results Card */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Classification Results
                </Typography>
                {classificationResult ? (
                  <Box>
                    <Typography variant="body1" gutterBottom>
                      Top Prediction: {classificationResult.top_prediction}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      Confidence: {(classificationResult.confidence_score * 100).toFixed(2)}%
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      Processing Time: {classificationResult.process_time_ms}ms
                    </Typography>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Upload and classify an image to see results
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* History Card */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Classification History
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View your past classification results
                </Typography>
                <Button 
                  variant="contained" 
                  sx={{ mt: 2 }}
                  onClick={() => navigate('/user/history')}
                >
                  View History
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default UserDashboard; 