from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Communication, User
from schemas.schemas import Communication as CommunicationSchema, CommunicationCreate, CommunicationUpdate
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[CommunicationSchema])
def read_communications(
    skip: int = 0,
    limit: int = 100,
    contact_id: Optional[int] = Query(None, description="Filter by contact ID"),
    type: Optional[str] = Query(None, description="Filter by communication type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Communication)
    
    if contact_id:
        query = query.filter(Communication.contact_id == contact_id)
    if type:
        query = query.filter(Communication.type == type)
    
    communications = query.offset(skip).limit(limit).all()
    return communications

@router.post("/", response_model=CommunicationSchema)
def create_communication(
    communication: CommunicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_communication = Communication(**communication.dict())
    db.add(db_communication)
    db.commit()
    db.refresh(db_communication)
    return db_communication

@router.get("/{communication_id}", response_model=CommunicationSchema)
def read_communication(
    communication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    communication = db.query(Communication).filter(Communication.id == communication_id).first()
    if communication is None:
        raise HTTPException(status_code=404, detail="Communication not found")
    return communication

@router.put("/{communication_id}", response_model=CommunicationSchema)
def update_communication(
    communication_id: int,
    communication_update: CommunicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    communication = db.query(Communication).filter(Communication.id == communication_id).first()
    if communication is None:
        raise HTTPException(status_code=404, detail="Communication not found")
    
    update_data = communication_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(communication, field, value)
    
    db.commit()
    db.refresh(communication)
    return communication

@router.delete("/{communication_id}")
def delete_communication(
    communication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    communication = db.query(Communication).filter(Communication.id == communication_id).first()
    if communication is None:
        raise HTTPException(status_code=404, detail="Communication not found")
    
    db.delete(communication)
    db.commit()
    return {"message": "Communication deleted successfully"}