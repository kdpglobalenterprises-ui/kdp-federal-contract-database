import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';

const schema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().required('Password is required'),
});

interface LoginFormData {
  email: string;
  password: string;
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: yupResolver(schema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError('');
    
    const success = await login(data.email, data.password);
    if (!success) {
      setError('Invalid email or password');
    }
    
    setLoading(false);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e3a8a 0%, #10b981 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <Card
          sx={{
            boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
            borderRadius: 3,
          }}
        >
          <CardContent sx={{ p: 6 }}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #1e3a8a 0%, #10b981 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '2rem',
                  mx: 'auto',
                  mb: 2,
                }}
              >
                KDP
              </Box>
              <Typography variant="h4" component="h1" fontWeight={600} gutterBottom>
                KDP Global
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Contract Brokerage System
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to access your federal contract opportunities
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
              <TextField
                {...register('email')}
                fullWidth
                label="Email Address"
                type="email"
                error={!!errors.email}
                helperText={errors.email?.message}
                margin="normal"
                autoComplete="email"
                autoFocus
                sx={{ mb: 2 }}
              />
              
              <TextField
                {...register('password')}
                fullWidth
                label="Password"
                type="password"
                error={!!errors.password}
                helperText={errors.password?.message}
                margin="normal"
                autoComplete="current-password"
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #1e3a8a 0%, #10b981 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1e40af 0%, #059669 100%)',
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Sign In'
                )}
              </Button>
            </Box>

            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Federal Contract Brokerage Database System
              </Typography>
              <Typography variant="caption" color="text.secondary">
                © 2025 KDP Global Enterprises. All rights reserved.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;