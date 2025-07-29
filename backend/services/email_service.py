import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict
from jinja2 import Template
from sqlalchemy.orm import Session
from database.models import EmailTemplate, ProcurementOfficer, Communication
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "kendrick@kdp-global.com")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
    def send_email(self, to_email: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send email with optional attachments"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.email_user, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def render_template(self, template_body: str, context: Dict) -> str:
        """Render email template with context variables"""
        try:
            template = Template(template_body)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template: {str(e)}")
            return template_body

    def send_introduction_email(self, db: Session, officer_id: int) -> bool:
        """Send introduction email to procurement officer"""
        officer = db.query(ProcurementOfficer).filter(ProcurementOfficer.id == officer_id).first()
        if not officer or not officer.email:
            return False
        
        template = db.query(EmailTemplate).filter(
            EmailTemplate.template_type == "introduction",
            EmailTemplate.is_active == True
        ).first()
        
        if not template:
            # Use default template
            subject = "Partnership Opportunity - KDP Global Contract Brokerage"
            body = self._get_default_introduction_template()
        else:
            subject = template.subject
            body = template.body
        
        context = {
            'officer_name': officer.name,
            'agency': officer.agency,
            'company_name': 'KDP Global Enterprises',
            'sender_name': 'Kendrick',
            'sender_email': self.email_user,
            'phone': '(555) 123-4567',  # Replace with actual phone
        }
        
        rendered_body = self.render_template(body, context)
        rendered_subject = self.render_template(subject, context)
        
        success = self.send_email(officer.email, rendered_subject, rendered_body)
        
        if success:
            # Log communication
            communication = Communication(
                contact_id=officer_id,
                date=datetime.utcnow(),
                type="email",
                subject=rendered_subject,
                outcome="Introduction email sent",
                follow_up_date=datetime.utcnow().date() + timedelta(days=3)
            )
            db.add(communication)
            db.commit()
        
        return success

    def send_follow_up_email(self, db: Session, officer_id: int, follow_up_type: str = "general") -> bool:
        """Send follow-up email to procurement officer"""
        officer = db.query(ProcurementOfficer).filter(ProcurementOfficer.id == officer_id).first()
        if not officer or not officer.email:
            return False
        
        template = db.query(EmailTemplate).filter(
            EmailTemplate.template_type == "follow_up",
            EmailTemplate.is_active == True
        ).first()
        
        if not template:
            # Use default template
            subject = "Following Up - KDP Global Partnership"
            body = self._get_default_follow_up_template()
        else:
            subject = template.subject
            body = template.body
        
        context = {
            'officer_name': officer.name,
            'agency': officer.agency,
            'company_name': 'KDP Global Enterprises',
            'sender_name': 'Kendrick',
            'sender_email': self.email_user,
            'follow_up_type': follow_up_type,
        }
        
        rendered_body = self.render_template(body, context)
        rendered_subject = self.render_template(subject, context)
        
        success = self.send_email(officer.email, rendered_subject, rendered_body)
        
        if success:
            # Log communication
            communication = Communication(
                contact_id=officer_id,
                date=datetime.utcnow(),
                type="email",
                subject=rendered_subject,
                outcome=f"Follow-up email sent ({follow_up_type})",
                follow_up_date=datetime.utcnow().date() + timedelta(days=7)
            )
            db.add(communication)
            db.commit()
        
        return success

    def send_opportunity_alert(self, db: Session, officer_id: int, contract_title: str, contract_value: float = None) -> bool:
        """Send opportunity alert email"""
        officer = db.query(ProcurementOfficer).filter(ProcurementOfficer.id == officer_id).first()
        if not officer or not officer.email:
            return False
        
        subject = f"New Contract Opportunity - {contract_title}"
        
        context = {
            'officer_name': officer.name,
            'contract_title': contract_title,
            'contract_value': f"${contract_value:,.2f}" if contract_value else "TBD",
            'company_name': 'KDP Global Enterprises',
            'sender_name': 'Kendrick',
        }
        
        body = self._get_opportunity_alert_template()
        rendered_body = self.render_template(body, context)
        
        success = self.send_email(officer.email, subject, rendered_body)
        
        if success:
            # Log communication
            communication = Communication(
                contact_id=officer_id,
                date=datetime.utcnow(),
                type="email",
                subject=subject,
                outcome="Opportunity alert sent",
                follow_up_date=datetime.utcnow().date() + timedelta(days=2)
            )
            db.add(communication)
            db.commit()
        
        return success

    def send_bulk_emails(self, db: Session, officer_ids: List[int], template_type: str) -> Dict[str, int]:
        """Send bulk emails to multiple officers"""
        results = {"sent": 0, "failed": 0}
        
        for officer_id in officer_ids:
            try:
                if template_type == "introduction":
                    success = self.send_introduction_email(db, officer_id)
                elif template_type == "follow_up":
                    success = self.send_follow_up_email(db, officer_id)
                else:
                    continue
                
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to send bulk email to officer {officer_id}: {str(e)}")
                results["failed"] += 1
        
        return results

    def check_follow_up_reminders(self, db: Session) -> List[Dict]:
        """Check for communications that need follow-up"""
        today = datetime.utcnow().date()
        
        # Find communications with follow-up dates today or overdue
        overdue_communications = db.query(Communication).filter(
            Communication.follow_up_date <= today
        ).all()
        
        reminders = []
        for comm in overdue_communications:
            officer = db.query(ProcurementOfficer).filter(
                ProcurementOfficer.id == comm.contact_id
            ).first()
            
            if officer:
                reminders.append({
                    'communication_id': comm.id,
                    'officer_id': officer.id,
                    'officer_name': officer.name,
                    'agency': officer.agency,
                    'last_contact': comm.date,
                    'follow_up_date': comm.follow_up_date,
                    'days_overdue': (today - comm.follow_up_date).days
                })
        
        return reminders

    def _get_default_introduction_template(self) -> str:
        """Default introduction email template"""
        return """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #1e3a8a 0%, #10b981 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">KDP Global Enterprises</h2>
                    <p style="margin: 5px 0 0 0;">Federal Contract Brokerage Services</p>
                </div>
                
                <p>Dear {{ officer_name }},</p>
                
                <p>I hope this email finds you well. My name is {{ sender_name }}, and I represent {{ company_name }}, a specialized federal contract brokerage firm.</p>
                
                <p>We focus on connecting qualified contractors with federal opportunities, particularly in the following NAICS codes:</p>
                <ul>
                    <li>488510 - Freight Transportation Arrangement</li>
                    <li>541614 - Process, Physical Distribution, and Logistics Consulting</li>
                    <li>332311 - Prefabricated Metal Building and Component Manufacturing</li>
                    <li>492110 - Couriers and Express Delivery Services</li>
                    <li>336611 - Ship Building and Repairing</li>
                </ul>
                
                <p>Given your role at {{ agency }}, I believe there may be opportunities for us to work together to ensure your procurement needs are met with qualified, reliable contractors.</p>
                
                <p>I would welcome the opportunity to discuss how KDP Global can support {{ agency }}'s contracting objectives. Would you be available for a brief call next week?</p>
                
                <p>Best regards,</p>
                <p><strong>{{ sender_name }}</strong><br>
                KDP Global Enterprises<br>
                Email: {{ sender_email }}<br>
                Phone: {{ phone }}</p>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #f8fafc; border-radius: 5px; font-size: 12px; color: #64748b;">
                    <p>This email is sent in accordance with federal procurement regulations. If you would prefer not to receive future communications, please reply with "UNSUBSCRIBE".</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _get_default_follow_up_template(self) -> str:
        """Default follow-up email template"""
        return """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #1e3a8a 0%, #10b981 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">KDP Global Enterprises</h2>
                    <p style="margin: 5px 0 0 0;">Federal Contract Brokerage Services</p>
                </div>
                
                <p>Dear {{ officer_name }},</p>
                
                <p>I wanted to follow up on my previous email regarding potential partnership opportunities between {{ company_name }} and {{ agency }}.</p>
                
                <p>As a federal contract brokerage firm, we maintain an extensive network of pre-qualified contractors across multiple industries. Our services include:</p>
                <ul>
                    <li>Contractor vetting and qualification</li>
                    <li>Proposal coordination and support</li>
                    <li>Project management and oversight</li>
                    <li>Compliance and reporting assistance</li>
                </ul>
                
                <p>We understand the challenges procurement officers face in finding reliable contractors who can deliver quality work on time and within budget. Our 3% brokerage fee structure ensures we're only successful when you are.</p>
                
                <p>I'd be happy to provide references from other agencies we've worked with or discuss specific upcoming opportunities.</p>
                
                <p>Would you have 15 minutes this week for a brief conversation?</p>
                
                <p>Best regards,</p>
                <p><strong>{{ sender_name }}</strong><br>
                KDP Global Enterprises<br>
                Email: {{ sender_email }}</p>
            </div>
        </body>
        </html>
        """

    def _get_opportunity_alert_template(self) -> str:
        """Opportunity alert email template"""
        return """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #1e3a8a 0%, #10b981 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">New Contract Opportunity</h2>
                    <p style="margin: 5px 0 0 0;">KDP Global Enterprises</p>
                </div>
                
                <p>Dear {{ officer_name }},</p>
                
                <p>I wanted to bring to your attention a new contract opportunity that may be of interest:</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1e3a8a; margin-top: 0;">{{ contract_title }}</h3>
                    <p><strong>Estimated Value:</strong> {{ contract_value }}</p>
                </div>
                
                <p>{{ company_name }} has identified several qualified contractors in our network who would be excellent candidates for this opportunity. We can provide:</p>
                
                <ul>
                    <li>Pre-qualified contractor recommendations</li>
                    <li>Proposal coordination and review</li>
                    <li>Project oversight and management</li>
                    <li>Compliance monitoring</li>
                </ul>
                
                <p>If this opportunity aligns with your agency's needs, I'd be happy to discuss our qualified contractors and their capabilities.</p>
                
                <p>Please let me know if you'd like more information.</p>
                
                <p>Best regards,</p>
                <p><strong>{{ sender_name }}</strong><br>
                KDP Global Enterprises</p>
            </div>
        </body>
        </html>
        """

# Initialize email service
email_service = EmailService()