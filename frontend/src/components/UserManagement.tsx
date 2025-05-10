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
  Switch,
  FormControlLabel,
  Alert,
  Button,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface User {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  mfa_enabled: boolean;
  is_email_verified: boolean;
  locked_until: string | null;
}

interface UserManagementProps {
  token: string;
}

const UserManagement: React.FC<UserManagementProps> = ({ token }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('https://localhost:8000/api/v1/user/list', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data);
    } catch (error) {
      setError('Failed to fetch users');
      console.error('Error fetching users:', error);
    }
  };

  const handleUpdateUser = async (userId: number, updates: Partial<User>) => {
    try {
      const response = await fetch(`https://localhost:8000/api/v1/user/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      setSuccess('User updated successfully');
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.user_id === userId 
            ? { ...user, ...updates } 
            : user
        )
      );
    } catch (error) {
      setError('Failed to update user');
      console.error('Error updating user:', error);
    }
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5">User Management</Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Full Name</TableCell>
              <TableCell>Active</TableCell>
              <TableCell>MFA Enabled</TableCell>
              <TableCell>Email Verified</TableCell>
              <TableCell>Locked Until</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.user_id}>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.full_name}</TableCell>
                <TableCell>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={user.is_active}
                        onChange={(e) =>
                          handleUpdateUser(user.user_id, { is_active: e.target.checked })
                        }
                      />
                    }
                    label=""
                  />
                </TableCell>
                <TableCell>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={user.mfa_enabled}
                        onChange={(e) =>
                          handleUpdateUser(user.user_id, { mfa_enabled: e.target.checked })
                        }
                      />
                    }
                    label=""
                  />
                </TableCell>
                <TableCell>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={user.is_email_verified}
                        onChange={(e) =>
                          handleUpdateUser(user.user_id, { is_email_verified: e.target.checked })
                        }
                      />
                    }
                    label=""
                  />
                </TableCell>
                <TableCell>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <DateTimePicker
                        value={user.locked_until ? new Date(user.locked_until) : null}
                        onChange={(date: Date | null) =>
                          handleUpdateUser(user.user_id, { locked_until: date?.toISOString() || null })
                        }
                        slotProps={{ textField: { size: 'small' } }}
                      />
                      {user.locked_until && (
                        <Button
                          variant="outlined"
                          size="small"
                          color="success"
                          onClick={() => handleUpdateUser(user.user_id, { locked_until: null })}
                        >
                          Unlock
                        </Button>
                      )}
                    </Box>
                  </LocalizationProvider>
                </TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleUpdateUser(user.user_id, {})}
                  >
                    Update
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default UserManagement; 