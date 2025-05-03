import { createContext, useContext, useState, ReactNode } from 'react';
import axios from 'axios';


interface AuthContextType {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<any>;
  verifyMFA: (userId: string, token: string) => Promise<void>;
  setupMFA: (userId: string) => Promise<any>;
  verifyMFASetup: (userId: string, token: string) => Promise<void>;
  logout: () => void;
  token: string | null;
  userType: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [userType, setUserType] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      console.log('Sending login request for username:', username);
      const response = await axios.post('http://localhost:8000/api/v1/auth/login', 
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      console.log('Login response:', response.data);
      
      // Set the token even if MFA is required
      if (response.data.access_token) {
        setToken(response.data.access_token);
        localStorage.setItem('token', response.data.access_token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const setupMFA = async (userId: string) => {
    try {
      const currentToken = token || localStorage.getItem('token');
      if (!currentToken) {
        throw new Error('No authentication token available');
      }

      const response = await axios.post('http://localhost:8000/api/v1/auth/setup-mfa', {}, {
        headers: {
          'Authorization': `Bearer ${currentToken}`
        }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const verifyMFASetup = async (userId: string, token: string) => {
    try {
      const currentToken = token || localStorage.getItem('token');
      if (!currentToken) {
        throw new Error('No authentication token available');
      }

      // Validate token format (should be 6 digits)
      if (!/^\d{6}$/.test(token)) {
        throw new Error('Invalid token format. Please enter a 6-digit code.');
      }

      // Ensure userId is a number and create the request data
      const requestData = {
        user_id: parseInt(userId, 10), // Ensure it's a base-10 integer
        token: token.trim() // Remove any whitespace
      };

      console.log('MFA Setup Verification Request:', {
        url: 'http://localhost:8000/api/v1/auth/verify-mfa-setup',
        data: requestData,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${currentToken}`
        }
      });

      const response = await axios.post(
        'http://localhost:8000/api/v1/auth/verify-mfa-setup',
        requestData,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${currentToken}`
          },
        }
      );

      console.log('MFA setup verification response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('MFA setup verification error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        requestData: {
          user_id: userId,
          token: token
        }
      });
      throw error;
    }
  };

  const verifyMFA = async (userId: string, token: string) => {
    try {
      // Create request data matching the MFAVerify schema
      const requestData = {
        user_id: parseInt(userId, 10), // Convert to integer
        token: token.trim() // Remove any whitespace
      };

      console.log('Sending MFA verification request:', requestData);

      const response = await axios.post(
        'http://localhost:8000/api/v1/auth/verify-mfa',
        requestData,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      console.log('MFA verification response:', response.data);

      setToken(response.data.access_token);
      setUserType(response.data.user_type);
      setIsAuthenticated(true);
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('userType', response.data.user_type);
    } catch (error: any) {
      console.error('MFA verification error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUserType(null);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
    localStorage.removeItem('userType');
  };

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      login, 
      verifyMFA, 
      setupMFA, 
      verifyMFASetup, 
      logout,
      token,
      userType
    }}>
      {children}
    </AuthContext.Provider>
  );
}; 