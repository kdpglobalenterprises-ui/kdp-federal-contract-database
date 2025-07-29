# KDP Global Federal Contract Brokerage System

A comprehensive web application designed for federal contract brokerage operations, featuring automated contract scraping, relationship management, revenue tracking, and professional analytics dashboard.

## 🚀 Features

### Core Functionality
- **Contract Management**: Complete CRUD operations for federal contracts with opportunity scoring (1-10 scale)
- **Automated Scraping**: Daily contract scraping from SAM.gov, Miami-Dade County portal, and Unison Marketplace
- **NAICS Code Filtering**: Targeted filtering for codes 488510, 541614, 332311, 492110, 336611
- **3% Brokerage Fee Calculations**: Automated fee calculations and revenue tracking
- **Professional Dashboard**: Real-time metrics, charts, and performance analytics

### Relationship Management
- **Prime Contractors**: Manage relationships with contact info, revenue ranges, employee counts
- **Subcontractors**: Directory with capabilities, certifications, performance ratings
- **Procurement Officers**: CRM with relationship strength tracking and communication history
- **Communications**: Log all interactions with automated follow-up reminders

### Automation & Integration
- **Email Templates**: Automated introduction, follow-up, and opportunity alert emails
- **Google Drive Integration**: Import existing contact data and automated backups
- **Daily Alerts**: Automated opportunity notifications and follow-up reminders
- **Export Functionality**: Excel/CSV export for all data tables

### Modern UI/UX
- **2025 Modern Design**: Navy blue/white/green color scheme matching KDP Global branding
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Dark/Light Mode**: User-selectable theme toggle
- **Interactive Charts**: Professional visualizations using Recharts
- **Clean Data Tables**: Sortable and filterable data grids

## 🏗️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with SQLAlchemy ORM
- **Celery + Redis**: Background task processing for scraping and notifications
- **BeautifulSoup + Selenium**: Web scraping for contract opportunities
- **JWT Authentication**: Secure user authentication and authorization

### Frontend
- **React 18**: Modern React with TypeScript for type safety
- **Material-UI (MUI)**: Professional component library with custom theming
- **React Query**: Efficient data fetching and caching
- **Recharts**: Beautiful and responsive chart components
- **React Hook Form**: Performant forms with validation

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis (for background tasks)
- Chrome/Chromium (for web scraping)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kdp-contract-brokerage
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb kdp_contracts
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

### Background Services

1. **Start Redis server**
   ```bash
   redis-server
   ```

2. **Start Celery worker** (in separate terminal)
   ```bash
   cd backend
   celery -A tasks worker --loglevel=info
   ```

3. **Start Celery beat scheduler** (in separate terminal)
   ```bash
   cd backend
   celery -A tasks beat --loglevel=info
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/kdp_contracts

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=kendrick@kdp-global.com
EMAIL_PASSWORD=your-app-password

# Google Drive Integration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# External APIs
SAM_GOV_API_KEY=your-sam-gov-api-key
MIAMI_DADE_API_KEY=your-miami-dade-api-key

# Application Settings
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=["http://localhost:3000"]
```

### Google Drive Integration

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Drive API

2. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create new service account
   - Download JSON credentials file as `credentials.json`

3. **Share Google Drive Folder**
   - Create a folder in Google Drive for contact data
   - Share folder with service account email
   - Copy folder ID from URL

### Email Configuration

1. **Gmail Setup**
   - Enable 2-factor authentication
   - Generate app-specific password
   - Use app password in EMAIL_PASSWORD

2. **Custom SMTP**
   - Update SMTP_SERVER and SMTP_PORT
   - Provide appropriate credentials

## 📊 Database Schema

### Core Tables
- **Contracts**: Contract opportunities with scoring and tracking
- **Prime_Contractors**: Prime contractor relationships and contact info
- **Subcontractors**: Subcontractor capabilities and performance
- **Procurement_Officers**: Government contact CRM
- **Communications**: Communication history and follow-ups
- **Revenue_Tracking**: Brokerage fees and financial performance

### Support Tables
- **Users**: System user authentication
- **Email_Templates**: Customizable email templates
- **Scraping_Logs**: Contract scraping audit trail

## 🤖 Automated Features

### Daily Contract Scraping
- **SAM.gov**: Federal contract opportunities via API
- **Miami-Dade County**: Local government contracts
- **Unison Marketplace**: Additional contract sources
- **NAICS Filtering**: Automatic filtering for target codes
- **Duplicate Prevention**: Smart duplicate detection and prevention

### Email Automation
- **Introduction Emails**: Automated outreach to new procurement officers
- **Follow-up Sequences**: 48-72 hour follow-up reminders
- **Opportunity Alerts**: Notify relevant contacts of new opportunities
- **Template System**: Customizable email templates with variables

### Notification System
- **Daily Opportunity Alerts**: Summary of new high-value contracts
- **Follow-up Reminders**: Overdue communication notifications
- **Performance Reports**: Weekly/monthly analytics summaries

## 📈 Analytics & Reporting

### Dashboard Metrics
- **Contract Pipeline**: Opportunity scoring and value tracking
- **Revenue Analytics**: Monthly revenue trends and projections
- **Success Rates**: Placement success and conversion metrics
- **Agency Performance**: Top agencies and relationship health
- **NAICS Analysis**: Performance by industry code

### Export Capabilities
- **Excel Export**: Formatted spreadsheets with charts
- **CSV Export**: Raw data for external analysis
- **PDF Reports**: Professional formatted reports
- **Google Drive Backup**: Automated data backups

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Admin and user role permissions
- **Data Encryption**: Sensitive data encryption at rest
- **Audit Logging**: Complete audit trail of system activities
- **Rate Limiting**: API rate limiting and abuse prevention

## 🚀 Deployment

### Production Deployment

1. **Setup Production Database**
   ```bash
   # PostgreSQL with connection pooling
   # Redis for caching and background tasks
   ```

2. **Configure Web Server**
   ```bash
   # Nginx reverse proxy configuration
   # SSL certificate setup
   # Static file serving
   ```

3. **Process Management**
   ```bash
   # Supervisor or systemd for process management
   # Gunicorn for WSGI serving
   # Celery workers and beat scheduler
   ```

4. **Environment Setup**
   ```bash
   # Production environment variables
   # Security configurations
   # Monitoring and logging
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is proprietary software developed for KDP Global Enterprises.

## 📞 Support

For support and questions, contact:
- **Email**: kendrick@kdp-global.com
- **Company**: KDP Global Enterprises
- **System**: Federal Contract Brokerage Platform

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
  - Contract management and scraping
  - Relationship CRM
  - Email automation
  - Analytics dashboard
  - Google Drive integration

---

**KDP Global Enterprises** - Federal Contract Brokerage System
*Connecting qualified contractors with federal opportunities*
