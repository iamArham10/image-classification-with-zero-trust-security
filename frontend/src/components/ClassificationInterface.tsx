import React, { useState, useEffect } from 'react';
import { Box, Button, Paper, Typography, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

interface ClassificationHistory {
  id: string;
  imageUrl: string;
  result: string;
  confidence: number;
  timestamp: string;
  status: string;
}

interface ClassificationInterfaceProps {
  onClassify: (image: File) => Promise<{ top_prediction: string; confidence_score: number }>;
  history: ClassificationHistory[];
  onHistoryItemClick: (item: ClassificationHistory) => void;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  margin: theme.spacing(2),
  height: 'calc(100vh - 100px)',
  display: 'flex',
  flexDirection: 'column',
}));

const HistoryList = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  marginTop: theme.spacing(2),
}));

const ClassificationInterface: React.FC<ClassificationInterfaceProps> = ({
  onClassify,
  history,
  onHistoryItemClick,
}) => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [classificationResult, setClassificationResult] = useState<{ prediction: string; confidence: number } | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedImage(event.target.files[0]);
      setClassificationResult(null);
    }
  };

  const handleClassify = async () => {
    if (selectedImage) {
      setIsLoading(true);
      try {
        const result = await onClassify(selectedImage);
        setClassificationResult({
          prediction: result.top_prediction,
          confidence: result.confidence_score
        });
      } catch (error) {
        console.error('Classification error:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const fetchImage = async (url: string, id: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch image');
      }
      
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      setImageUrls(prev => ({ ...prev, [id]: objectUrl }));
    } catch (error) {
      console.error('Error fetching image:', error);
    }
  };

  useEffect(() => {
    // Cleanup object URLs when component unmounts
    return () => {
      Object.values(imageUrls).forEach(url => URL.revokeObjectURL(url));
    };
  }, []);

  useEffect(() => {
    // Fetch images for history items
    history.forEach(item => {
      if (!imageUrls[item.id]) {
        fetchImage(item.imageUrl, item.id);
      }
    });
  }, [history]);

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      <Box sx={{ width: '250px', p: 2, borderRight: '1px solid #ccc' }}>
        <Button
          variant="contained"
          fullWidth
          onClick={() => setShowHistory(false)}
          sx={{ mb: 2 }}
        >
          Classify Image
        </Button>
        <HistoryList>
          {history.map((item) => (
            <Paper
              key={item.id}
              sx={{ 
                p: 1, 
                mb: 1, 
                cursor: 'pointer',
                backgroundColor: item.status === 'success' ? '#e8f5e9' : 
                               item.status === 'failed' ? '#ffebee' : '#fff3e0'
              }}
              onClick={() => {
                onHistoryItemClick(item);
                setShowHistory(true);
              }}
            >
              <Typography variant="body2">{item.timestamp}</Typography>
              <Typography variant="body2" noWrap>
                {item.result} ({(item.confidence * 100).toFixed(2)}%)
              </Typography>
            </Paper>
          ))}
        </HistoryList>
      </Box>

      <Box sx={{ flex: 1, p: 2 }}>
        {!showHistory ? (
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Image Classification
            </Typography>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ marginBottom: '16px' }}
            />
            {selectedImage && (
              <Box sx={{ mb: 2 }}>
                <img
                  src={URL.createObjectURL(selectedImage)}
                  alt="Selected"
                  style={{ maxWidth: '100%', maxHeight: '300px' }}
                />
              </Box>
            )}
            <Button
              variant="contained"
              onClick={handleClassify}
              disabled={!selectedImage || isLoading}
              sx={{ mb: 2 }}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Classify'}
            </Button>
            {classificationResult && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Classification Result:</Typography>
                <Typography variant="body1">
                  {classificationResult.prediction} ({(classificationResult.confidence * 100).toFixed(2)}%)
                </Typography>
              </Box>
            )}
          </StyledPaper>
        ) : (
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Classification History
            </Typography>
            {history.map((item) => (
              <Paper 
                key={item.id} 
                sx={{ 
                  p: 2, 
                  mb: 2,
                  backgroundColor: item.status === 'success' ? '#e8f5e9' : 
                                 item.status === 'failed' ? '#ffebee' : '#fff3e0'
                }}
              >
                <Typography variant="subtitle1">{item.timestamp}</Typography>
                <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                  {imageUrls[item.id] ? (
                    <img
                      src={imageUrls[item.id]}
                      alt="History"
                      style={{ maxWidth: '200px', maxHeight: '200px' }}
                    />
                  ) : (
                    <CircularProgress size={24} />
                  )}
                  <Box>
                    <Typography variant="h6">Result:</Typography>
                    <Typography>{item.result} ({(item.confidence * 100).toFixed(2)}%)</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Status: {item.status}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            ))}
          </StyledPaper>
        )}
      </Box>
    </Box>
  );
};

export default ClassificationInterface; 