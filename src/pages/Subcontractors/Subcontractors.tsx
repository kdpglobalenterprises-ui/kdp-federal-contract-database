import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Subcontractors: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
        Subcontractors
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Directory of qualified subcontractors with capabilities and performance ratings.
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Subcontractor Network
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Comprehensive database of subcontractors including capabilities, certifications, 
            performance ratings, geographic coverage, and contact information.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Subcontractors;