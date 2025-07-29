from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Subcontractor, User
from schemas.schemas import Subcontractor as SubcontractorSchema, SubcontractorCreate, SubcontractorUpdate
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[SubcontractorSchema])
def read_subcontractors(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search in company name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Subcontractor)
    
    if search:
        query = query.filter(Subcontractor.company_name.ilike(f"%{search}%"))
    
    subcontractors = query.offset(skip).limit(limit).all()
    return subcontractors

@router.post("/", response_model=SubcontractorSchema)
def create_subcontractor(
    subcontractor: SubcontractorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_subcontractor = Subcontractor(**subcontractor.dict())
    db.add(db_subcontractor)
    db.commit()
    db.refresh(db_subcontractor)
    return db_subcontractor

@router.get("/{subcontractor_id}", response_model=SubcontractorSchema)
def read_subcontractor(
    subcontractor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subcontractor = db.query(Subcontractor).filter(Subcontractor.id == subcontractor_id).first()
    if subcontractor is None:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    return subcontractor

@router.put("/{subcontractor_id}", response_model=SubcontractorSchema)
def update_subcontractor(
    subcontractor_id: int,
    subcontractor_update: SubcontractorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subcontractor = db.query(Subcontractor).filter(Subcontractor.id == subcontractor_id).first()
    if subcontractor is None:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    
    update_data = subcontractor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subcontractor, field, value)
    
    db.commit()
    db.refresh(subcontractor)
    return subcontractor

@router.delete("/{subcontractor_id}")
def delete_subcontractor(
    subcontractor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subcontractor = db.query(Subcontractor).filter(Subcontractor.id == subcontractor_id).first()
    if subcontractor is None:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    
    db.delete(subcontractor)
    db.commit()
    return {"message": "Subcontractor deleted successfully"}