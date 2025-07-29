from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    agency = Column(String(200), nullable=False)
    naics_code = Column(String(10), nullable=False)
    value = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")
    opportunity_score = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    revenue_tracking = relationship("RevenueTracking", back_populates="contract")

class PrimeContractor(Base):
    __tablename__ = "prime_contractors"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    revenue_range = Column(String(50), nullable=True)
    employee_count = Column(Integer, nullable=True)
    address = Column(Text, nullable=True)
    relationship_status = Column(String(50), default="prospect")  # prospect, active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subcontractor(Base):
    __tablename__ = "subcontractors"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False)
    capabilities = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    performance_rating = Column(Float, nullable=True)  # 1-10 scale
    geographic_coverage = Column(String(200), nullable=True)
    contact_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProcurementOfficer(Base):
    __tablename__ = "procurement_officers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    agency = Column(String(200), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    last_contact_date = Column(Date, nullable=True)
    relationship_strength = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    communications = relationship("Communication", back_populates="contact")

class Communication(Base):
    __tablename__ = "communications"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("procurement_officers.id"))
    date = Column(DateTime, nullable=False)
    type = Column(String(50), nullable=False)  # email, phone, meeting, etc.
    subject = Column(String(200), nullable=True)
    outcome = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("ProcurementOfficer", back_populates="communications")

class RevenueTracking(Base):
    __tablename__ = "revenue_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    placement_date = Column(Date, nullable=False)
    fee_amount = Column(Float, nullable=False)
    success_rate = Column(Float, nullable=True)  # percentage
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract", back_populates="revenue_tracking")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)  # SAM.gov, Miami-Dade, etc.
    contracts_found = Column(Integer, default=0)
    contracts_added = Column(Integer, default=0)
    status = Column(String(50), nullable=False)  # success, error, partial
    error_message = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    template_type = Column(String(50), nullable=False)  # introduction, follow_up, reminder
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)