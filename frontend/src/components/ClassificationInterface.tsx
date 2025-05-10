import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Paper, 
  Typography, 
  CircularProgress, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia, 
  Chip, 
  Divider, 
  IconButton,
  Tooltip,
  useTheme,
  LinearProgress,
  Badge
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import HistoryIcon from '@mui/icons-material/History';
import ImageIcon from '@mui/icons-material/Image';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

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

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius * 2,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
}));

const HistoryList = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  marginTop: theme.spacing(2),
  padding: theme.spacing(1),
  '&::-webkit-scrollbar': {
    width: '6px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#f1f1f1',
    borderRadius: '10px',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#888',
    borderRadius: '10px',
  },
  '&::-webkit-scrollbar-thumb:hover': {
    background: '#555',
  },
}));

const UploadZone = styled(Box)(({ theme }) => ({
  border: `2px dashed ${theme.palette.primary.main}`,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  backgroundColor: `${theme.palette.primary.main}10`,
  '&:hover': {
    backgroundColor: `${theme.palette.primary.main}20`,
    borderColor: theme.palette.primary.dark,
  },
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
  const [selectedHistoryItem, setSelectedHistoryItem] = useState<ClassificationHistory | null>(null);
  const theme = useTheme();

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

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'success':
        return <CheckCircleIcon sx={{ color: theme.palette.success.main }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: theme.palette.error.main }} />;
      default:
        return <WarningIcon sx={{ color: theme.palette.warning.main }} />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return theme.palette.success.main;
    if (confidence >= 0.6) return theme.palette.info.main;
    if (confidence >= 0.4) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const renderClassificationView = () => (
    <StyledPaper>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
          Image Classification
        </Typography>
        <Tooltip title="View History">
          <IconButton 
            color="primary" 
            onClick={() => setShowHistory(true)}
            sx={{ 
              backgroundColor: `${theme.palette.primary.main}10`,
              '&:hover': {
                backgroundColor: `${theme.palette.primary.main}20`,
              }
            }}
          >
            <Badge badgeContent={history.length} color="primary">
              <HistoryIcon />
            </Badge>
          </IconButton>
        </Tooltip>
      </Box>
      
      <Divider sx={{ mb: 3 }} />
      
      {!selectedImage ? (
        <UploadZone 
          onClick={() => document.getElementById('image-upload')?.click()}
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            justifyContent: 'center',
            height: 300,
            mb: 3
          }}
        >
          <CloudUploadIcon sx={{ fontSize: 60, color: theme.palette.primary.main, mb: 2 }} />
          <Typography variant="h6" color="primary" gutterBottom>
            Click or drag to upload an image
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supported formats: JPG, PNG, JPEG
          </Typography>
          <Button
            component="label"
            variant="contained"
            sx={{ mt: 2 }}
            startIcon={<ImageIcon />}
          >
            Select Image
            <VisuallyHiddenInput 
              id="image-upload"
              type="file" 
              accept="image/*" 
              onChange={handleImageUpload}
            />
          </Button>
        </UploadZone>
      ) : (
        <Box sx={{ mb: 3 }}>
          <Card sx={{ mb: 3, overflow: 'hidden' }}>
            <CardMedia
              component="img"
              image={URL.createObjectURL(selectedImage)}
              alt="Selected"
              sx={{ 
                maxHeight: '300px', 
                objectFit: 'contain',
                backgroundColor: '#f5f5f5',
                p: 2
              }}
            />
            <CardContent sx={{ py: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {selectedImage.name} ({(selectedImage.size / 1024).toFixed(2)} KB)
              </Typography>
            </CardContent>
          </Card>
          
          <Button
            variant="contained"
            fullWidth
            onClick={handleClassify}
            disabled={isLoading}
            sx={{ 
              py: 1.5,
              fontWeight: 600,
              boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',
            }}
          >
            {isLoading ? (
              <>
                <CircularProgress size={24} sx={{ mr: 1, color: 'white' }} />
                Classifying...
              </>
            ) : 'Classify Image'}
          </Button>
          
          <Button
            variant="outlined"
            fullWidth
            onClick={() => {
              setSelectedImage(null);
              setClassificationResult(null);
            }}
            sx={{ mt: 1, py: 1 }}
          >
            Clear
          </Button>
        </Box>
      )}
      
      {classificationResult && (
        <Card 
          sx={{ 
            mt: 2, 
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${getConfidenceColor(classificationResult.confidence)}20`
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
              Classification Result
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 600, mr: 1 }}>
                Prediction:
              </Typography>
              <Chip 
                label={classificationResult.prediction} 
                color="primary" 
                sx={{ fontWeight: 600 }}
              />
            </Box>
            
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">Confidence:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: getConfidenceColor(classificationResult.confidence) }}>
                  {(classificationResult.confidence * 100).toFixed(2)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={classificationResult.confidence * 100} 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  backgroundColor: `${getConfidenceColor(classificationResult.confidence)}20`,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getConfidenceColor(classificationResult.confidence)
                  }
                }}
              />
            </Box>
            
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
              <InfoIcon sx={{ color: theme.palette.info.main, mr: 1, fontSize: 20 }} />
              <Typography variant="body2" color="text.secondary">
                {classificationResult.confidence >= 0.8 
                  ? 'High confidence prediction. The model is very certain about this result.'
                  : classificationResult.confidence >= 0.6
                    ? 'Good confidence prediction. The model is reasonably certain about this result.'
                    : classificationResult.confidence >= 0.4
                      ? 'Moderate confidence prediction. The model is somewhat uncertain about this result.'
                      : 'Low confidence prediction. The model is uncertain about this result.'}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </StyledPaper>
  );

  const renderHistoryView = () => (
    <StyledPaper>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton 
            onClick={() => {
              setShowHistory(false);
              setSelectedHistoryItem(null);
            }}
            sx={{ mr: 1 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h5" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
            {selectedHistoryItem ? 'Classification Details' : 'Classification History'}
          </Typography>
        </Box>
        {selectedHistoryItem && (
          <Chip 
            icon={getStatusIcon(selectedHistoryItem.status)} 
            label={selectedHistoryItem.status.toUpperCase()} 
            color={selectedHistoryItem.status === 'success' ? 'success' : selectedHistoryItem.status === 'failed' ? 'error' : 'warning'}
          />
        )}
      </Box>
      
      <Divider sx={{ mb: 3 }} />
      
      {selectedHistoryItem ? (
        <Box>
          <Card sx={{ mb: 3, overflow: 'hidden' }}>
            {imageUrls[selectedHistoryItem.id] ? (
              <CardMedia
                component="img"
                image={imageUrls[selectedHistoryItem.id]}
                alt="History"
                sx={{ 
                  maxHeight: '300px', 
                  objectFit: 'contain',
                  backgroundColor: '#f5f5f5',
                  p: 2
                }}
              />
            ) : (
              <Box sx={{ height: 200, display: 'flex', justifyContent: 'center', alignItems: 'center', bgcolor: '#f5f5f5' }}>
                <CircularProgress />
              </Box>
            )}
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {selectedHistoryItem.timestamp}
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="body1" sx={{ fontWeight: 600, mr: 1 }}>
                  Prediction:
                </Typography>
                <Chip 
                  label={selectedHistoryItem.result} 
                  color="primary" 
                  sx={{ fontWeight: 600 }}
                />
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Confidence:</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: getConfidenceColor(selectedHistoryItem.confidence) }}>
                    {(selectedHistoryItem.confidence * 100).toFixed(2)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={selectedHistoryItem.confidence * 100} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 4,
                    backgroundColor: `${getConfidenceColor(selectedHistoryItem.confidence)}20`,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getConfidenceColor(selectedHistoryItem.confidence)
                    }
                  }}
                />
              </Box>
              
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <InfoIcon sx={{ color: theme.palette.info.main, mr: 1, fontSize: 20 }} />
                <Typography variant="body2" color="text.secondary">
                  {selectedHistoryItem.confidence >= 0.8 
                    ? 'High confidence prediction. The model is very certain about this result.'
                    : selectedHistoryItem.confidence >= 0.6
                      ? 'Good confidence prediction. The model is reasonably certain about this result.'
                      : selectedHistoryItem.confidence >= 0.4
                        ? 'Moderate confidence prediction. The model is somewhat uncertain about this result.'
                        : 'Low confidence prediction. The model is uncertain about this result.'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
          
          <Button
            variant="outlined"
            fullWidth
            onClick={() => setSelectedHistoryItem(null)}
            sx={{ mt: 1 }}
          >
            Back to History
          </Button>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {history.length > 0 ? (
            history.map((item) => (
              <Grid key={item.id} xs={12} sm={6} md={4} component="div">
                <Card 
                  sx={{ 
                    cursor: 'pointer', 
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 10px 20px rgba(0,0,0,0.1)'
                    },
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    borderLeft: `4px solid ${
                      item.status === 'success' 
                        ? theme.palette.success.main 
                        : item.status === 'failed' 
                          ? theme.palette.error.main 
                          : theme.palette.warning.main
                    }`
                  }}
                  onClick={() => setSelectedHistoryItem(item)}
                >
                  {imageUrls[item.id] ? (
                    <CardMedia
                      component="img"
                      image={imageUrls[item.id]}
                      alt="History"
                      sx={{ 
                        height: 140, 
                        objectFit: 'cover',
                      }}
                    />
                  ) : (
                    <Box sx={{ height: 140, display: 'flex', justifyContent: 'center', alignItems: 'center', bgcolor: '#f5f5f5' }}>
                      <CircularProgress size={30} />
                    </Box>
                  )}
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }} noWrap>
                        {item.result}
                      </Typography>
                      <Tooltip title={`Status: ${item.status}`}>
                        {getStatusIcon(item.status)}
                      </Tooltip>
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {(item.confidence * 100).toFixed(2)}% confidence
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      {item.timestamp}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid xs={12} component="div">
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <HistoryIcon sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  No classification history yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Classify some images to see your history here
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={() => setShowHistory(false)}
                >
                  Classify an Image
                </Button>
              </Box>
            </Grid>
          )}
        </Grid>
      )}
    </StyledPaper>
  );

  return (
    <Box sx={{ height: '100%' }}>
      {showHistory ? renderHistoryView() : renderClassificationView()}
    </Box>
  );
};

export default ClassificationInterface;