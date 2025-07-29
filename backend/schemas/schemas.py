from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# Contract Schemas
class ContractBase(BaseModel):
    title: str
    agency: str
    naics_code: str
    value: Optional[float] = None
    deadline: Optional[datetime] = None
    status: str = "active"
    opportunity_score: Optional[int] = None
    notes: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    title: Optional[str] = None
    agency: Optional[str] = None
    naics_code: Optional[str] = None
    value: Optional[float] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    opportunity_score: Optional[int] = None
    notes: Optional[str] = None

class Contract(ContractBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Prime Contractor Schemas
class PrimeContractorBase(BaseModel):
    company_name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    revenue_range: Optional[str] = None
    employee_count: Optional[int] = None
    address: Optional[str] = None
    relationship_status: str = "prospect"

class PrimeContractorCreate(PrimeContractorBase):
    pass

class PrimeContractorUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    revenue_range: Optional[str] = None
    employee_count: Optional[int] = None
    address: Optional[str] = None
    relationship_status: Optional[str] = None

class PrimeContractor(PrimeContractorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Subcontractor Schemas
class SubcontractorBase(BaseModel):
    company_name: str
    capabilities: Optional[str] = None
    certifications: Optional[str] = None
    performance_rating: Optional[float] = None
    geographic_coverage: Optional[str] = None
    contact_info: Optional[str] = None

class SubcontractorCreate(SubcontractorBase):
    pass

class SubcontractorUpdate(BaseModel):
    company_name: Optional[str] = None
    capabilities: Optional[str] = None
    certifications: Optional[str] = None
    performance_rating: Optional[float] = None
    geographic_coverage: Optional[str] = None
    contact_info: Optional[str] = None

class Subcontractor(SubcontractorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Procurement Officer Schemas
class ProcurementOfficerBase(BaseModel):
    name: str
    agency: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    last_contact_date: Optional[date] = None
    relationship_strength: Optional[int] = None
    notes: Optional[str] = None

class ProcurementOfficerCreate(ProcurementOfficerBase):
    pass

class ProcurementOfficerUpdate(BaseModel):
    name: Optional[str] = None
    agency: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    last_contact_date: Optional[date] = None
    relationship_strength: Optional[int] = None
    notes: Optional[str] = None

class ProcurementOfficer(ProcurementOfficerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Communication Schemas
class CommunicationBase(BaseModel):
    contact_id: int
    date: datetime
    type: str
    subject: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_date: Optional[date] = None

class CommunicationCreate(CommunicationBase):
    pass

class CommunicationUpdate(BaseModel):
    contact_id: Optional[int] = None
    date: Optional[datetime] = None
    type: Optional[str] = None
    subject: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_date: Optional[date] = None

class Communication(CommunicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Revenue Tracking Schemas
class RevenueTrackingBase(BaseModel):
    contract_id: int
    placement_date: date
    fee_amount: float
    success_rate: Optional[float] = None

class RevenueTrackingCreate(RevenueTrackingBase):
    pass

class RevenueTrackingUpdate(BaseModel):
    contract_id: Optional[int] = None
    placement_date: Optional[date] = None
    fee_amount: Optional[float] = None
    success_rate: Optional[float] = None

class RevenueTracking(RevenueTrackingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Email Template Schemas
class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    body: str
    template_type: str
    is_active: bool = True

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    template_type: Optional[str] = None
    is_active: Optional[bool] = None

class EmailTemplate(EmailTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_contracts: int
    active_contracts: int
    total_revenue: float
    success_rate: float
    top_agencies: List[dict]
    monthly_revenue: List[dict]
    opportunity_pipeline: List[dict]

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None