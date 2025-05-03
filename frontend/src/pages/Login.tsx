import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  Tabs,
  Tab,
  Grid,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

type LoginState = 'login' | 'mfa-setup' | 'mfa-verify' | 'mfa-setup-verify' | 'email-verify';
type ViewType = 'login' | 'signup';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [mfaToken, setMfaToken] = useState('');
  const [loginState, setLoginState] = useState<LoginState>('login');
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const [mfaSetupData, setMfaSetupData] = useState<{ secret: string; qr_code: string } | null>(null);
  const [currentView, setCurrentView] = useState<ViewType>('login');
  const [verificationCode, setVerificationCode] = useState('');
  const [verificationError, setVerificationError] = useState('');
  const [verificationSent, setVerificationSent] = useState(false);
  const navigate = useNavigate();
  const { login, verifyMFA, setupMFA, verifyMFASetup } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log('Attempting login for username:', username);
      const response = await login(username, password);
      console.log('Login response received:', response);
      
      if (!response.user_id) {
        console.error('No user_id in response:', response);
        setError('Login failed: No user ID received');
        return;
      }
      
      if (response.requires_mfa) {
        setLoginState('mfa-verify');
        setUserId(response.user_id.toString());
      } else if (!response.is_email_verified) {
        setLoginState('email-verify');
        setUserId(response.user_id.toString());
        await sendVerificationEmail();
      } else {
        const setupResponse = await setupMFA(response.user_id.toString());
        setMfaSetupData(setupResponse);
        setUserId(response.user_id.toString());
        setLoginState('mfa-setup');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
          email,
          full_name: fullName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signup failed');
      }

      // Clear form and show success message
      setUsername('');
      setPassword('');
      setConfirmPassword('');
      setEmail('');
      setFullName('');
      setError('');
      setCurrentView('login');
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    }
  };

  const handleMFAVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await verifyMFA(userId, mfaToken);
      // The DashboardRedirect component will handle the redirection based on user type
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'MFA verification failed');
    }
  };

  const handleMFASetupVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) {
      setError('User ID is missing. Please try logging in again.');
      return;
    }
    try {
      console.log('Verifying MFA setup with:', { userId, mfaToken });
      await verifyMFASetup(userId, mfaToken);
      setLoginState('mfa-verify');
      setMfaToken('');
    } catch (err: any) {
      console.error('MFA setup verification error:', err);
      setError(err.response?.data?.detail || 'MFA setup verification failed');
    }
  };

  const sendVerificationEmail = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/send-verification-email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to send verification email');
      }
      
      setVerificationSent(true);
      setVerificationError('');
    } catch (err: any) {
      setVerificationError(err.message || 'Failed to send verification email');
    }
  };

  const handleEmailVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          code: verificationCode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      // After successful verification, proceed with MFA setup
      const setupResponse = await setupMFA(userId);
      setMfaSetupData(setupResponse);
      setLoginState('mfa-setup');
      setVerificationCode('');
      setVerificationError('');
    } catch (err: any) {
      setVerificationError(err.message || 'Verification failed');
    }
  };

  const renderLoginForm = () => (
    <Box component="form" onSubmit={handleLogin}>
      <TextField
        margin="normal"
        required
        fullWidth
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Sign In
      </Button>
    </Box>
  );

  const renderSignupForm = () => (
    <Box component="form" onSubmit={handleSignup}>
      <TextField
        margin="normal"
        required
        fullWidth
        label="Full Name"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        helperText="Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character"
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Confirm Password"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Sign Up
      </Button>
    </Box>
  );

  const renderMFASetup = () => (
    <Box>
      <Typography variant="body1" gutterBottom>
        Please scan this QR code with your authenticator app:
      </Typography>
      {mfaSetupData && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <img src={mfaSetupData.qr_code} alt="MFA QR Code" />
        </Box>
      )}
      <Typography variant="body2" gutterBottom>
        Or enter this code manually: {mfaSetupData?.secret}
      </Typography>
      <Box component="form" onSubmit={handleMFASetupVerify}>
        <TextField
          margin="normal"
          required
          fullWidth
          label="Enter the code from your authenticator app"
          value={mfaToken}
          onChange={(e) => setMfaToken(e.target.value)}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
        >
          Verify Setup
        </Button>
      </Box>
    </Box>
  );

  const renderMFAVerify = () => (
    <Box component="form" onSubmit={handleMFAVerify}>
      <Typography variant="body1" gutterBottom>
        Please enter the code from your authenticator app
      </Typography>
      <TextField
        margin="normal"
        required
        fullWidth
        label="MFA Code"
        value={mfaToken}
        onChange={(e) => setMfaToken(e.target.value)}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Verify
      </Button>
    </Box>
  );

  const renderEmailVerification = () => (
    <Box component="form" onSubmit={handleEmailVerification}>
      <Typography variant="body1" gutterBottom>
        Please verify your email address. A verification code has been sent to your email.
      </Typography>
      {verificationSent && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Verification email sent successfully
        </Alert>
      )}
      {verificationError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {verificationError}
        </Alert>
      )}
      <TextField
        margin="normal"
        required
        fullWidth
        label="Verification Code"
        value={verificationCode}
        onChange={(e) => setVerificationCode(e.target.value)}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Verify Email
      </Button>
      <Button
        fullWidth
        variant="outlined"
        onClick={sendVerificationEmail}
        sx={{ mb: 2 }}
      >
        Resend Verification Code
      </Button>
    </Box>
  );

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Image Classification
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loginState === 'login' && (
            <>
              <Tabs
                value={currentView}
                onChange={(_, newValue) => {
                  setCurrentView(newValue);
                  setError('');
                }}
                centered
                sx={{ mb: 3 }}
              >
                <Tab label="Login" value="login" />
                <Tab label="Sign Up" value="signup" />
              </Tabs>

              {currentView === 'login' ? renderLoginForm() : renderSignupForm()}
            </>
          )}
          {loginState === 'mfa-setup' && renderMFASetup()}
          {loginState === 'mfa-verify' && renderMFAVerify()}
          {loginState === 'email-verify' && renderEmailVerification()}
        </Paper>
      </Box>
    </Container>
  );
};

export default Login; 