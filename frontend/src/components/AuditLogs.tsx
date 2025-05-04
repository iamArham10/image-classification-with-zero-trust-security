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
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
} from '@mui/material';

interface AuditLogUserInfo {
  username: string | null;
  user_type: string | null;
}

interface AuditLog {
  log_id: number;
  timestamp: string;
  user_id: number | null;
  ip_address: string | null;
  user_agent: string | null;
  action: string;
  resource: string | null;
  status: string;
  details: string | null;
  user_info: AuditLogUserInfo | null;
}

interface AuditLogsProps {
  token: string;
}

const AuditLogs: React.FC<AuditLogsProps> = ({ token }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 10;

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/v1/audit/list?limit=${limit}&offset=${page * limit}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch audit logs');
      }

      const data = await response.json();
      setLogs(data.content);
      setTotalCount(data.total_count);
    } catch (error) {
      setError('Failed to fetch audit logs');
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, token]);

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log);
  };

  const handleCloseDetails = () => {
    setSelectedLog(null);
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Typography variant="h5" gutterBottom>
        Audit Logs
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>User Type</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Status</TableCell>
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
                <TableRow key={log.log_id}>
                  <TableCell>
                    {new Date(log.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>{log.user_info?.username || 'N/A'}</TableCell>
                  <TableCell>{log.user_info?.user_type || 'N/A'}</TableCell>
                  <TableCell>{log.action}</TableCell>
                  <TableCell>{log.resource || 'N/A'}</TableCell>
                  <TableCell>{log.status}</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleViewDetails(log)}
                    >
                      View Details
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

      <Dialog open={!!selectedLog} onClose={handleCloseDetails} maxWidth="md">
        <DialogTitle>Audit Log Details</DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Timestamp:</strong> {new Date(selectedLog.timestamp).toLocaleString()}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>User ID:</strong> {selectedLog.user_id || 'N/A'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Username:</strong> {selectedLog.user_info?.username || 'N/A'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>User Type:</strong> {selectedLog.user_info?.user_type || 'N/A'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>IP Address:</strong> {selectedLog.ip_address || 'N/A'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>User Agent:</strong> {selectedLog.user_agent || 'N/A'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Action:</strong> {selectedLog.action}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Resource:</strong> {selectedLog.resource || 'N/A'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Status:</strong> {selectedLog.status}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Details:</strong> {selectedLog.details || 'No details available'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditLogs; 