import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Switch,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Alert,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { TextFieldProps } from '@mui/material/TextField';

interface Admin {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  mfa_enabled: boolean;
  is_email_verified: boolean;
  locked_until: string | null;
}

interface AdminManagementProps {
  token: string;
}

const AdminManagement: React.FC<AdminManagementProps> = ({ token }) => {
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [newAdmin, setNewAdmin] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    admin_creation_token: '',
  });

  useEffect(() => {
    fetchAdmins();
  }, []);

  const fetchAdmins = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/admin/list', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch admins');
      }

      const data = await response.json();
      setAdmins(data);
    } catch (error) {
      setError('Failed to fetch admins');
      console.error('Error fetching admins:', error);
    }
  };

  const handleUpdateAdmin = async (adminId: number, updates: Partial<Admin>) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/admin/${adminId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error('Failed to update admin');
      }

      setSuccess('Admin updated successfully');
      setAdmins(prevAdmins => 
        prevAdmins.map(admin => 
          admin.user_id === adminId 
            ? { ...admin, ...updates } 
            : admin
        )
      );
    } catch (error) {
      setError('Failed to update admin');
      console.error('Error updating admin:', error);
    }
  };

  const handleUnlockAdmin = async (adminId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/admin/${adminId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ locked_until: null }),
      });

      if (!response.ok) {
        throw new Error('Failed to unlock admin');
      }

      setSuccess('Admin unlocked successfully');
      setAdmins(prevAdmins => 
        prevAdmins.map(admin => 
          admin.user_id === adminId 
            ? { ...admin, locked_until: null } 
            : admin
        )
      );
    } catch (error) {
      setError('Failed to unlock admin');
      console.error('Error unlocking admin:', error);
    }
  };

  const handleCreateAdmin = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/admin/create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAdmin),
      });

      if (!response.ok) {
        throw new Error('Failed to create admin');
      }

      setSuccess('Admin created successfully');
      setOpenCreateDialog(false);
      setNewAdmin({
        username: '',
        email: '',
        password: '',
        full_name: '',
        admin_creation_token: '',
      });
      fetchAdmins();
    } catch (error) {
      setError('Failed to create admin');
      console.error('Error creating admin:', error);
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
        <Typography variant="h5">Admin Management</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setOpenCreateDialog(true)}
        >
          Create New Admin
        </Button>
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
            {admins.map((admin) => (
              <TableRow key={admin.user_id}>
                <TableCell>{admin.username}</TableCell>
                <TableCell>{admin.email}</TableCell>
                <TableCell>{admin.full_name}</TableCell>
                <TableCell>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={admin.is_active}
                        onChange={(e) =>
                          handleUpdateAdmin(admin.user_id, { is_active: e.target.checked })
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
                        checked={admin.mfa_enabled}
                        onChange={(e) =>
                          handleUpdateAdmin(admin.user_id, { mfa_enabled: e.target.checked })
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
                        checked={admin.is_email_verified}
                        onChange={(e) =>
                          handleUpdateAdmin(admin.user_id, { is_email_verified: e.target.checked })
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
                        value={admin.locked_until ? new Date(admin.locked_until) : null}
                        onChange={(date: Date | null) =>
                          handleUpdateAdmin(admin.user_id, { locked_until: date?.toISOString() || null })
                        }
                        slotProps={{ textField: { size: 'small' } }}
                      />
                      {admin.locked_until && (
                        <Button
                          variant="outlined"
                          size="small"
                          color="success"
                          onClick={() => handleUnlockAdmin(admin.user_id)}
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
                    onClick={() => handleUpdateAdmin(admin.user_id, {})}
                  >
                    Update
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)}>
        <DialogTitle>Create New Admin</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Username"
              value={newAdmin.username}
              onChange={(e) => setNewAdmin({ ...newAdmin, username: e.target.value })}
              fullWidth
            />
            <TextField
              label="Email"
              type="email"
              value={newAdmin.email}
              onChange={(e) => setNewAdmin({ ...newAdmin, email: e.target.value })}
              fullWidth
            />
            <TextField
              label="Password"
              type="password"
              value={newAdmin.password}
              onChange={(e) => setNewAdmin({ ...newAdmin, password: e.target.value })}
              fullWidth
            />
            <TextField
              label="Full Name"
              value={newAdmin.full_name}
              onChange={(e) => setNewAdmin({ ...newAdmin, full_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Admin Creation Token"
              value={newAdmin.admin_creation_token}
              onChange={(e) => setNewAdmin({ ...newAdmin, admin_creation_token: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateAdmin} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminManagement; 