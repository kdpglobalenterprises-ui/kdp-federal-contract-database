from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import ProcurementOfficer, User
from schemas.schemas import ProcurementOfficer as ProcurementOfficerSchema, ProcurementOfficerCreate, ProcurementOfficerUpdate
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[ProcurementOfficerSchema])
def read_procurement_officers(
    skip: int = 0,
    limit: int = 100,
    agency: Optional[str] = Query(None, description="Filter by agency"),
    search: Optional[str] = Query(None, description="Search in name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ProcurementOfficer)
    
    if agency:
        query = query.filter(ProcurementOfficer.agency.ilike(f"%{agency}%"))
    if search:
        query = query.filter(ProcurementOfficer.name.ilike(f"%{search}%"))
    
    officers = query.offset(skip).limit(limit).all()
    return officers

@router.post("/", response_model=ProcurementOfficerSchema)
def create_procurement_officer(
    officer: ProcurementOfficerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_officer = ProcurementOfficer(**officer.dict())
    db.add(db_officer)
    db.commit()
    db.refresh(db_officer)
    return db_officer

@router.get("/{officer_id}", response_model=ProcurementOfficerSchema)
def read_procurement_officer(
    officer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    officer = db.query(ProcurementOfficer).filter(ProcurementOfficer.id == officer_id).first()
    if officer is None:
        raise HTTPException(status_code=404, detail="Procurement officer not found")
    return officer

@router.put("/{officer_id}", response_model=ProcurementOfficerSchema)
def update_procurement_officer(
    officer_id: int,
    officer_update: ProcurementOfficerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    officer = db.query(ProcurementOfficer).filter(ProcurementOfficer.id == officer_id).first()
    if officer is None:
        raise HTTPException(status_code=404, detail="Procurement officer not found")
    
    update_data = officer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(officer, field, value)
    
    db.commit()
    db.refresh(officer)
    return officer

@router.delete("/{officer_id}")
def delete_procurement_officer(
    officer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    officer = db.query(ProcurementOfficer).filter(ProcurementOfficer.id == officer_id).first()
    if officer is None:
        raise HTTPException(status_code=404, detail="Procurement officer not found")
    
    db.delete(officer)
    db.commit()
    return {"message": "Procurement officer deleted successfully"}