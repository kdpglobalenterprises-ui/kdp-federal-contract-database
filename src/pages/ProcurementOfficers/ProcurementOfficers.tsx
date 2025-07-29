import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const ProcurementOfficers: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
        Procurement Officers
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Build and maintain relationships with key procurement decision makers.
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Procurement Officer CRM
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Contact management system for procurement officers including relationship strength tracking, 
            last contact dates, agencies, and communication history.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProcurementOfficers;