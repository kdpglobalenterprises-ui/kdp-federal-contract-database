import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const PrimeContractors: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
        Prime Contractors
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage relationships with prime contractors and track partnership opportunities.
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Prime Contractor Database
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Full CRUD interface for managing prime contractor relationships, contact information, 
            revenue ranges, employee counts, and relationship status tracking.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PrimeContractors;