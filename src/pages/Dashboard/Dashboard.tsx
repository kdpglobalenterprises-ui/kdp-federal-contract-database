import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  Assignment,
  AttachMoney,
  Business,
  Assessment,
  Notifications,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useQuery } from 'react-query';
import axios from 'axios';

// Mock data for demonstration
const mockStats = {
  total_contracts: 156,
  active_contracts: 89,
  total_revenue: 245000,
  success_rate: 67.5,
  top_agencies: [
    { agency: 'Department of Defense', contract_count: 23, total_value: 1200000 },
    { agency: 'Department of Transportation', contract_count: 18, total_value: 890000 },
    { agency: 'GSA', contract_count: 15, total_value: 750000 },
    { agency: 'Department of Energy', contract_count: 12, total_value: 650000 },
    { agency: 'NASA', contract_count: 8, total_value: 420000 },
  ],
  monthly_revenue: [
    { month: 'Jan', revenue: 18000 },
    { month: 'Feb', revenue: 22000 },
    { month: 'Mar', revenue: 25000 },
    { month: 'Apr', revenue: 19000 },
    { month: 'May', revenue: 28000 },
    { month: 'Jun', revenue: 31000 },
  ],
  opportunity_pipeline: [
    { score: 9, count: 12, total_value: 2400000 },
    { score: 8, count: 18, total_value: 1800000 },
    { score: 7, count: 25, total_value: 1500000 },
    { score: 6, count: 20, total_value: 1200000 },
    { score: 5, count: 14, total_value: 800000 },
  ],
};

const mockRecentActivity = {
  recent_contracts: [
    { id: 1, title: 'IT Support Services', agency: 'DOD', value: 150000, created_at: '2025-01-08' },
    { id: 2, title: 'Logistics Management', agency: 'DOT', value: 89000, created_at: '2025-01-07' },
    { id: 3, title: 'Facility Maintenance', agency: 'GSA', value: 75000, created_at: '2025-01-06' },
  ],
  recent_revenue: [
    { id: 1, fee_amount: 4500, placement_date: '2025-01-05' },
    { id: 2, fee_amount: 2670, placement_date: '2025-01-04' },
    { id: 3, fee_amount: 2250, placement_date: '2025-01-03' },
  ],
};

const COLORS = ['#1e3a8a', '#3b82f6', '#10b981', '#34d399', '#f59e0b'];

const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode; color?: string }> = ({
  title,
  value,
  icon,
  color = 'primary.main',
}) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography color="text.secondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h4" component="div" fontWeight={600}>
            {value}
          </Typography>
        </Box>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: 2,
            p: 1.5,
            color: 'white',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  // In a real app, these would be actual API calls
  const { data: stats } = useQuery('dashboard-stats', () => Promise.resolve(mockStats));
  const { data: recentActivity } = useQuery('recent-activity', () => Promise.resolve(mockRecentActivity));

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Welcome to your federal contract brokerage dashboard. Monitor opportunities, track revenue, and manage relationships.
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Contracts"
            value={stats?.total_contracts || 0}
            icon={<Assignment />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Contracts"
            value={stats?.active_contracts || 0}
            icon={<TrendingUp />}
            color="secondary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Revenue"
            value={formatCurrency(stats?.total_revenue || 0)}
            icon={<AttachMoney />}
            color="#f59e0b"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${stats?.success_rate || 0}%`}
            icon={<Assessment />}
            color="#8b5cf6"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Monthly Revenue Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Monthly Revenue Trend
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stats?.monthly_revenue || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="#1e3a8a"
                      strokeWidth={3}
                      dot={{ fill: '#1e3a8a', strokeWidth: 2, r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Agencies */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Top Agencies
              </Typography>
              <List>
                {stats?.top_agencies?.slice(0, 5).map((agency, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Business color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={agency.agency}
                      secondary={`${agency.contract_count} contracts • ${formatCurrency(agency.total_value)}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Opportunity Pipeline */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Opportunity Pipeline
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats?.opportunity_pipeline || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="score" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Bar dataKey="total_value" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Recent Activity
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Latest Contracts
                </Typography>
                {recentActivity?.recent_contracts?.map((contract) => (
                  <Box key={contract.id} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2" fontWeight={600}>
                      {contract.title}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      <Chip label={contract.agency} size="small" color="primary" />
                      <Typography variant="caption" color="text.secondary">
                        {formatCurrency(contract.value)}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Recent Revenue
                </Typography>
                {recentActivity?.recent_revenue?.map((revenue) => (
                  <Box key={revenue.id} sx={{ mb: 1, display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">
                      Placement Fee
                    </Typography>
                    <Typography variant="body2" fontWeight={600} color="secondary.main">
                      {formatCurrency(revenue.fee_amount)}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Quick Actions & Alerts
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'info.light', color: 'info.contrastText' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Notifications />
                      <Typography variant="body2" fontWeight={600}>
                        12 Follow-ups Due Today
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'warning.light', color: 'warning.contrastText' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TrendingUp />
                      <Typography variant="body2" fontWeight={600}>
                        5 High-Value Opportunities
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Assignment />
                      <Typography variant="body2" fontWeight={600}>
                        3 New Contracts Today
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;