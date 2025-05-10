import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  Tabs,
  Tab,
  Card,
  CardContent,
  Divider,
  Avatar,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import SecurityIcon from '@mui/icons-material/Security';

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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, verifyMFA, setupMFA, verifyMFASetup } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      console.log('Attempting login for username:', username);
      const response = await login(username, password);
      console.log('Login response received:', response);
      
      if (!response.user_id) {
        console.error('No user_id in response:', response);
        setError('Login failed: No user ID received');
        setIsLoading(false);
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
      setIsLoading(false);
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed');
      setIsLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        setIsLoading(false);
        return;
      }

      const response = await fetch('https://localhost:8000/api/v1/auth/signup', {
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
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'Signup failed');
      setIsLoading(false);
    }
  };

  const handleMFAVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await verifyMFA(userId, mfaToken);
      // The DashboardRedirect component will handle the redirection based on user type
      navigate('/dashboard');
      setIsLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'MFA verification failed');
      setIsLoading(false);
    }
  };

  const handleMFASetupVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    if (!userId) {
      setError('User ID is missing. Please try logging in again.');
      setIsLoading(false);
      return;
    }
    try {
      console.log('Verifying MFA setup with:', { userId, mfaToken });
      await verifyMFASetup(userId, mfaToken);
      setLoginState('mfa-verify');
      setMfaToken('');
      setIsLoading(false);
    } catch (err: any) {
      console.error('MFA setup verification error:', err);
      setError(err.response?.data?.detail || 'MFA setup verification failed');
      setIsLoading(false);
    }
  };

  const sendVerificationEmail = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('https://localhost:8000/api/v1/auth/send-verification-email', {
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
      setIsLoading(false);
    } catch (err: any) {
      setVerificationError(err.message || 'Failed to send verification email');
      setIsLoading(false);
    }
  };

  const handleEmailVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('https://localhost:8000/api/v1/auth/verify-email', {
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
      setIsLoading(false);
    } catch (err: any) {
      setVerificationError(err.message || 'Verification failed');
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const renderLoginForm = () => (
    <Box component="form" onSubmit={handleLogin} sx={{ mt: 2 }}>
      <TextField
        margin="normal"
        required
        fullWidth
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <PersonIcon color="primary" />
            </InputAdornment>
          ),
        }}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Password"
        type={showPassword ? "text" : "password"}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <LockOutlinedIcon color="primary" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={togglePasswordVisibility}
                edge="end"
              >
                {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2, py: 1.2 }}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
      </Button>
    </Box>
  );

  const renderSignupForm = () => (
    <Box component="form" onSubmit={handleSignup} sx={{ mt: 2 }}>
      <TextField
        margin="normal"
        required
        fullWidth
        label="Full Name"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <PersonIcon color="primary" />
            </InputAdornment>
          ),
        }}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <EmailIcon color="primary" />
            </InputAdornment>
          ),
        }}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <PersonIcon color="primary" />
            </InputAdornment>
          ),
        }}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Password"
        type={showPassword ? "text" : "password"}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        helperText="Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <LockOutlinedIcon color="primary" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={togglePasswordVisibility}
                edge="end"
              >
                {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        label="Confirm Password"
        type={showConfirmPassword ? "text" : "password"}
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <LockOutlinedIcon color="primary" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={toggleConfirmPasswordVisibility}
                edge="end"
              >
                {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2, py: 1.2 }}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Sign Up'}
      </Button>
    </Box>
  );

  const renderMFASetup = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="body1" gutterBottom>
        Please scan this QR code with your authenticator app:
      </Typography>
      {mfaSetupData && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3, p: 2, border: '1px dashed #ccc', borderRadius: 1 }}>
          <img src={mfaSetupData.qr_code} alt="MFA QR Code" style={{ maxWidth: '100%' }} />
        </Box>
      )}
      <Typography variant="body2" gutterBottom sx={{ mb: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        Or enter this code manually: <strong>{mfaSetupData?.secret}</strong>
      </Typography>
      <Box component="form" onSubmit={handleMFASetupVerify}>
        <TextField
          margin="normal"
          required
          fullWidth
          label="Enter the code from your authenticator app"
          value={mfaToken}
          onChange={(e) => setMfaToken(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SecurityIcon color="primary" />
              </InputAdornment>
            ),
          }}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2, py: 1.2 }}
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={24} /> : 'Verify Setup'}
        </Button>
      </Box>
    </Box>
  );

  const renderMFAVerify = () => (
    <Box component="form" onSubmit={handleMFAVerify} sx={{ mt: 2 }}>
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
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SecurityIcon color="primary" />
            </InputAdornment>
          ),
        }}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2, py: 1.2 }}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Verify'}
      </Button>
    </Box>
  );

  const renderEmailVerification = () => (
    <Box component="form" onSubmit={handleEmailVerification} sx={{ mt: 2 }}>
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
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <EmailIcon color="primary" />
            </InputAdornment>
          ),
        }}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2, py: 1.2 }}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Verify Email'}
      </Button>
      <Button
        fullWidth
        variant="outlined"
        onClick={sendVerificationEmail}
        sx={{ mb: 2, py: 1.2 }}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Resend Verification Code'}
      </Button>
    </Box>
  );

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%)',
        py: 4,
      }}
    >
      <Container component="main" maxWidth="sm">
        <Card elevation={5} sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <CardContent sx={{ p: 4 }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 56, height: 56 }}>
                <LockOutlinedIcon fontSize="large" />
              </Avatar>
              <Typography component="h1" variant="h4" sx={{ mt: 2, fontWeight: 600 }}>
                Image Classification
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Secure authentication with zero-trust security
              </Typography>
              
              <Divider sx={{ width: '100%', mb: 3 }} />
              
              {error && (
                <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
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
                    variant="fullWidth"
                    sx={{ mb: 2, width: '100%' }}
                    TabIndicatorProps={{
                      style: {
                        height: 3,
                      },
                    }}
                  >
                    <Tab label="Login" value="login" sx={{ fontWeight: 600 }} />
                    <Tab label="Sign Up" value="signup" sx={{ fontWeight: 600 }} />
                  </Tabs>

                  {currentView === 'login' ? renderLoginForm() : renderSignupForm()}
                </>
              )}
              {loginState === 'mfa-setup' && renderMFASetup()}
              {loginState === 'mfa-verify' && renderMFAVerify()}
              {loginState === 'email-verify' && renderEmailVerification()}
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;