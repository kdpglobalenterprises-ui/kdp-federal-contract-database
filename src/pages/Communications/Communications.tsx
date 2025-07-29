import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Communications: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
        Communications
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Track all communications and manage follow-up sequences.
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Communication Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Log and track all communications including emails, phone calls, meetings, 
            with automated follow-up reminders and email templates.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Communications;