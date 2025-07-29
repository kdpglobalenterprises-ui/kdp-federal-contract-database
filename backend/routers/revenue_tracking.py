from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import RevenueTracking, User
from schemas.schemas import RevenueTracking as RevenueTrackingSchema, RevenueTrackingCreate, RevenueTrackingUpdate
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[RevenueTrackingSchema])
def read_revenue_tracking(
    skip: int = 0,
    limit: int = 100,
    contract_id: Optional[int] = Query(None, description="Filter by contract ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(RevenueTracking)
    
    if contract_id:
        query = query.filter(RevenueTracking.contract_id == contract_id)
    
    revenue_records = query.offset(skip).limit(limit).all()
    return revenue_records

@router.post("/", response_model=RevenueTrackingSchema)
def create_revenue_tracking(
    revenue: RevenueTrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_revenue = RevenueTracking(**revenue.dict())
    db.add(db_revenue)
    db.commit()
    db.refresh(db_revenue)
    return db_revenue

@router.get("/{revenue_id}", response_model=RevenueTrackingSchema)
def read_revenue_tracking_record(
    revenue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    revenue = db.query(RevenueTracking).filter(RevenueTracking.id == revenue_id).first()
    if revenue is None:
        raise HTTPException(status_code=404, detail="Revenue tracking record not found")
    return revenue

@router.put("/{revenue_id}", response_model=RevenueTrackingSchema)
def update_revenue_tracking(
    revenue_id: int,
    revenue_update: RevenueTrackingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    revenue = db.query(RevenueTracking).filter(RevenueTracking.id == revenue_id).first()
    if revenue is None:
        raise HTTPException(status_code=404, detail="Revenue tracking record not found")
    
    update_data = revenue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(revenue, field, value)
    
    db.commit()
    db.refresh(revenue)
    return revenue

@router.delete("/{revenue_id}")
def delete_revenue_tracking(
    revenue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    revenue = db.query(RevenueTracking).filter(RevenueTracking.id == revenue_id).first()
    if revenue is None:
        raise HTTPException(status_code=404, detail="Revenue tracking record not found")
    
    db.delete(revenue)
    db.commit()
    return {"message": "Revenue tracking record deleted successfully"}