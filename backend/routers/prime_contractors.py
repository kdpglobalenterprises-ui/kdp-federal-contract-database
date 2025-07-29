from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import PrimeContractor, User
from schemas.schemas import PrimeContractor as PrimeContractorSchema, PrimeContractorCreate, PrimeContractorUpdate
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[PrimeContractorSchema])
def read_prime_contractors(
    skip: int = 0,
    limit: int = 100,
    relationship_status: Optional[str] = Query(None, description="Filter by relationship status"),
    search: Optional[str] = Query(None, description="Search in company name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PrimeContractor)
    
    if relationship_status:
        query = query.filter(PrimeContractor.relationship_status == relationship_status)
    if search:
        query = query.filter(PrimeContractor.company_name.ilike(f"%{search}%"))
    
    contractors = query.offset(skip).limit(limit).all()
    return contractors

@router.post("/", response_model=PrimeContractorSchema)
def create_prime_contractor(
    contractor: PrimeContractorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_contractor = PrimeContractor(**contractor.dict())
    db.add(db_contractor)
    db.commit()
    db.refresh(db_contractor)
    return db_contractor

@router.get("/{contractor_id}", response_model=PrimeContractorSchema)
def read_prime_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contractor = db.query(PrimeContractor).filter(PrimeContractor.id == contractor_id).first()
    if contractor is None:
        raise HTTPException(status_code=404, detail="Prime contractor not found")
    return contractor

@router.put("/{contractor_id}", response_model=PrimeContractorSchema)
def update_prime_contractor(
    contractor_id: int,
    contractor_update: PrimeContractorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contractor = db.query(PrimeContractor).filter(PrimeContractor.id == contractor_id).first()
    if contractor is None:
        raise HTTPException(status_code=404, detail="Prime contractor not found")
    
    update_data = contractor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contractor, field, value)
    
    db.commit()
    db.refresh(contractor)
    return contractor

@router.delete("/{contractor_id}")
def delete_prime_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contractor = db.query(PrimeContractor).filter(PrimeContractor.id == contractor_id).first()
    if contractor is None:
        raise HTTPException(status_code=404, detail="Prime contractor not found")
    
    db.delete(contractor)
    db.commit()
    return {"message": "Prime contractor deleted successfully"}