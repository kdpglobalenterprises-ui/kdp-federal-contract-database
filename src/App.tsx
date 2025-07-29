import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import Contracts from './pages/Contracts/Contracts';
import PrimeContractors from './pages/PrimeContractors/PrimeContractors';
import Subcontractors from './pages/Subcontractors/Subcontractors';
import ProcurementOfficers from './pages/ProcurementOfficers/ProcurementOfficers';
import Communications from './pages/Communications/Communications';
import RevenueTracking from './pages/RevenueTracking/RevenueTracking';
import Login from './pages/Auth/Login';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider as CustomThemeProvider } from './contexts/ThemeContext';

const queryClient = new QueryClient();

// KDP Global color scheme - Navy blue, white, green
const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: '#1e3a8a', // Navy blue
      light: '#3b82f6',
      dark: '#1e40af',
    },
    secondary: {
      main: '#10b981', // Green
      light: '#34d399',
      dark: '#059669',
    },
    background: {
      default: mode === 'light' ? '#f8fafc' : '#0f172a',
      paper: mode === 'light' ? '#ffffff' : '#1e293b',
    },
    text: {
      primary: mode === 'light' ? '#1e293b' : '#f1f5f9',
      secondary: mode === 'light' ? '#64748b' : '#94a3b8',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: mode === 'light' 
            ? '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)'
            : '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        },
      },
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/" /> : <Login />
      } />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/contracts" element={
        <ProtectedRoute>
          <Layout>
            <Contracts />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/prime-contractors" element={
        <ProtectedRoute>
          <Layout>
            <PrimeContractors />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/subcontractors" element={
        <ProtectedRoute>
          <Layout>
            <Subcontractors />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/procurement-officers" element={
        <ProtectedRoute>
          <Layout>
            <ProcurementOfficers />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/communications" element={
        <ProtectedRoute>
          <Layout>
            <Communications />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/revenue-tracking" element={
        <ProtectedRoute>
          <Layout>
            <RevenueTracking />
          </Layout>
        </ProtectedRoute>
      } />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CustomThemeProvider>
          {({ theme, toggleTheme }) => (
            <ThemeProvider theme={createAppTheme(theme)}>
              <CssBaseline />
              <Router>
                <AppRoutes />
              </Router>
              <Toaster 
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: theme === 'dark' ? '#1e293b' : '#ffffff',
                    color: theme === 'dark' ? '#f1f5f9' : '#1e293b',
                  },
                }}
              />
            </ThemeProvider>
          )}
        </CustomThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;