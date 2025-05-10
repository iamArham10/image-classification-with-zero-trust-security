import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogContent,
  CircularProgress,
  Alert,
} from '@mui/material';

interface ClassificationLog {
  classification_id: number;
  user_name: string;
  user_email: string;
  user_type: string;
  image_hash: string;
  original_filename: string;
  classification_timestamp: string;
  top_prediction: string;
  confidence_score: number;
  process_time_ms: number;
  status: string;
}

interface ClassificationLogsProps {
  token: string;
}

const ClassificationLogs: React.FC<ClassificationLogsProps> = ({ token }) => {
  const [logs, setLogs] = useState<ClassificationLog[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 10;

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `https://localhost:8000/api/v1/classification/history-all?limit=${limit}&offset=${page * limit}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch classification logs');
      }

      const data = await response.json();
      setLogs(data.content);
      setTotalCount(data.total_count);
    } catch (error) {
      setError('Failed to fetch classification logs');
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, token]);

  const handleViewImage = async (classificationId: number) => {
    try {
      const response = await fetch(
        `https://localhost:8000/api/v1/classification/image/${classificationId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch image');
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      setSelectedImage(objectUrl);
    } catch (error) {
      setError('Failed to fetch image');
      console.error('Error fetching image:', error);
    }
  };

  const handleCloseImage = () => {
    if (selectedImage) {
      URL.revokeObjectURL(selectedImage);
      setSelectedImage(null);
    }
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Typography variant="h5" gutterBottom>
        Classification Logs
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Timestamp</TableCell>
              <TableCell>Prediction</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Process Time</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : (
              logs.map((log) => (
                <TableRow key={log.classification_id}>
                  <TableCell>
                    {log.user_name} ({log.user_email})
                  </TableCell>
                  <TableCell>
                    {new Date(log.classification_timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>{log.top_prediction}</TableCell>
                  <TableCell>{(log.confidence_score * 100).toFixed(2)}%</TableCell>
                  <TableCell>{log.status}</TableCell>
                  <TableCell>{log.process_time_ms}ms</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleViewImage(log.classification_id)}
                    >
                      View Image
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button
          variant="contained"
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
        >
          Previous
        </Button>
        <Button
          variant="contained"
          disabled={(page + 1) * limit >= totalCount}
          onClick={() => setPage(page + 1)}
        >
          Next
        </Button>
      </Box>

      <Dialog open={!!selectedImage} onClose={handleCloseImage} maxWidth="md">
        <DialogContent>
          {selectedImage && (
            <img
              src={selectedImage}
              alt="Classification"
              style={{ maxWidth: '100%', maxHeight: '80vh' }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default ClassificationLogs; 