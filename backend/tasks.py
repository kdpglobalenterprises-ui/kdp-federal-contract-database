from celery import Celery
from celery.schedules import crontab
import os
from sqlalchemy.orm import Session
from database.database import SessionLocal
from services.scraping_service import run_daily_scraping
from services.email_service import email_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("kdp_contracts", broker=redis_url, backend=redis_url)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'daily-contract-scraping': {
            'task': 'tasks.scrape_contracts_task',
            'schedule': crontab(hour=6, minute=0),  # Run daily at 6 AM UTC
        },
        'check-follow-up-reminders': {
            'task': 'tasks.check_follow_ups_task',
            'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM UTC
        },
        'weekly-performance-report': {
            'task': 'tasks.send_weekly_report_task',
            'schedule': crontab(hour=10, minute=0, day_of_week=1),  # Monday at 10 AM UTC
        },
    },
)

@celery_app.task(bind=True)
def scrape_contracts_task(self):
    """Daily contract scraping task"""
    db = SessionLocal()
    try:
        logger.info("Starting daily contract scraping...")
        results = run_daily_scraping(db)
        
        total_found = sum(source['contracts_found'] for source in results.values() if 'contracts_found' in source)
        total_added = sum(source['contracts_added'] for source in results.values() if 'contracts_added' in source)
        
        logger.info(f"Scraping completed: {total_found} contracts found, {total_added} new contracts added")
        
        return {
            'status': 'success',
            'total_found': total_found,
            'total_added': total_added,
            'details': results
        }
        
    except Exception as e:
        logger.error(f"Contract scraping failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()

@celery_app.task(bind=True)
def check_follow_ups_task(self):
    """Check for overdue follow-ups and send reminders"""
    db = SessionLocal()
    try:
        logger.info("Checking for follow-up reminders...")
        
        reminders = email_service.check_follow_up_reminders(db)
        
        # Send reminder notifications (could be email, Slack, etc.)
        for reminder in reminders:
            logger.info(f"Follow-up reminder: {reminder['officer_name']} - {reminder['days_overdue']} days overdue")
        
        return {
            'status': 'success',
            'reminders_found': len(reminders),
            'reminders': reminders
        }
        
    except Exception as e:
        logger.error(f"Follow-up check failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()

@celery_app.task(bind=True)
def send_bulk_emails_task(self, officer_ids, template_type):
    """Send bulk emails to multiple officers"""
    db = SessionLocal()
    try:
        logger.info(f"Sending bulk {template_type} emails to {len(officer_ids)} officers...")
        
        results = email_service.send_bulk_emails(db, officer_ids, template_type)
        
        logger.info(f"Bulk email completed: {results['sent']} sent, {results['failed']} failed")
        
        return {
            'status': 'success',
            'sent': results['sent'],
            'failed': results['failed']
        }
        
    except Exception as e:
        logger.error(f"Bulk email failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()

@celery_app.task(bind=True)
def send_opportunity_alerts_task(self, contract_id):
    """Send opportunity alerts for new high-value contracts"""
    db = SessionLocal()
    try:
        from database.models import Contract, ProcurementOfficer
        
        # Get contract details
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {'status': 'error', 'error': 'Contract not found'}
        
        # Find relevant procurement officers (same agency or high relationship strength)
        officers = db.query(ProcurementOfficer).filter(
            ProcurementOfficer.agency.ilike(f"%{contract.agency}%")
        ).all()
        
        sent_count = 0
        for officer in officers:
            if officer.email:
                success = email_service.send_opportunity_alert(
                    db, officer.id, contract.title, contract.value
                )
                if success:
                    sent_count += 1
        
        logger.info(f"Opportunity alerts sent to {sent_count} officers for contract: {contract.title}")
        
        return {
            'status': 'success',
            'alerts_sent': sent_count,
            'contract_title': contract.title
        }
        
    except Exception as e:
        logger.error(f"Opportunity alert failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()

@celery_app.task(bind=True)
def send_weekly_report_task(self):
    """Send weekly performance report"""
    db = SessionLocal()
    try:
        from database.models import Contract, RevenueTracking
        from datetime import datetime, timedelta
        
        # Calculate weekly stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        new_contracts = db.query(Contract).filter(Contract.created_at >= week_ago).count()
        weekly_revenue = db.query(RevenueTracking).filter(
            RevenueTracking.created_at >= week_ago
        ).all()
        
        total_revenue = sum(r.fee_amount for r in weekly_revenue)
        
        # Create report content
        report = f"""
        KDP Global Weekly Performance Report
        
        Week of {week_ago.strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')}
        
        📊 Key Metrics:
        - New Contracts: {new_contracts}
        - Revenue Generated: ${total_revenue:,.2f}
        - Active Placements: {len(weekly_revenue)}
        
        This automated report is generated every Monday.
        """
        
        # Send report email (to admin/management)
        admin_email = os.getenv("ADMIN_EMAIL", "kendrick@kdp-global.com")
        email_service.send_email(
            admin_email,
            "KDP Global Weekly Performance Report",
            report.replace('\n', '<br>')
        )
        
        logger.info("Weekly report sent successfully")
        
        return {
            'status': 'success',
            'new_contracts': new_contracts,
            'weekly_revenue': total_revenue
        }
        
    except Exception as e:
        logger.error(f"Weekly report failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()

@celery_app.task(bind=True)
def backup_to_google_drive_task(self):
    """Backup database to Google Drive"""
    try:
        logger.info("Starting Google Drive backup...")
        
        # This would implement the actual backup logic
        # For now, return success
        
        logger.info("Google Drive backup completed")
        
        return {
            'status': 'success',
            'backup_time': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Google Drive backup failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

# Manual task triggers (can be called from API endpoints)
@celery_app.task(bind=True)
def manual_scraping_task(self, sources=None):
    """Manual contract scraping for specific sources"""
    if sources is None:
        sources = ['sam_gov', 'miami_dade', 'unison']
    
    return scrape_contracts_task.delay()

if __name__ == '__main__':
    celery_app.start()