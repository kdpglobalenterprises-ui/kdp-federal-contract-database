from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from database.database import get_db
from database.models import Contract, User
from schemas.schemas import Contract as ContractSchema, ContractCreate, ContractUpdate
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[ContractSchema])
def read_contracts(
    skip: int = 0,
    limit: int = 100,
    naics_code: Optional[str] = Query(None, description="Filter by NAICS code"),
    agency: Optional[str] = Query(None, description="Filter by agency"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_value: Optional[float] = Query(None, description="Minimum contract value"),
    max_value: Optional[float] = Query(None, description="Maximum contract value"),
    search: Optional[str] = Query(None, description="Search in title and notes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Contract)
    
    # Apply filters
    if naics_code:
        query = query.filter(Contract.naics_code == naics_code)
    if agency:
        query = query.filter(Contract.agency.ilike(f"%{agency}%"))
    if status:
        query = query.filter(Contract.status == status)
    if min_value:
        query = query.filter(Contract.value >= min_value)
    if max_value:
        query = query.filter(Contract.value <= max_value)
    if search:
        query = query.filter(or_(
            Contract.title.ilike(f"%{search}%"),
            Contract.notes.ilike(f"%{search}%")
        ))
    
    contracts = query.offset(skip).limit(limit).all()
    return contracts

@router.get("/naics-codes")
def get_target_naics_codes():
    """Get the target NAICS codes for filtering"""
    return {
        "naics_codes": [
            {"code": "488510", "description": "Freight Transportation Arrangement"},
            {"code": "541614", "description": "Process, Physical Distribution, and Logistics Consulting Services"},
            {"code": "332311", "description": "Prefabricated Metal Building and Component Manufacturing"},
            {"code": "492110", "description": "Couriers and Express Delivery Services"},
            {"code": "336611", "description": "Ship Building and Repairing"}
        ]
    }

@router.post("/", response_model=ContractSchema)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_contract = Contract(**contract.dict())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@router.get("/{contract_id}", response_model=ContractSchema)
def read_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.put("/{contract_id}", response_model=ContractSchema)
def update_contract(
    contract_id: int,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    update_data = contract_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)
    
    db.commit()
    db.refresh(contract)
    return contract

@router.delete("/{contract_id}")
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    db.delete(contract)
    db.commit()
    return {"message": "Contract deleted successfully"}

@router.post("/{contract_id}/calculate-fee")
def calculate_brokerage_fee(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if contract.value is None:
        raise HTTPException(status_code=400, detail="Contract value not set")
    
    fee_amount = contract.value * 0.03  # 3% brokerage fee
    
    return {
        "contract_id": contract_id,
        "contract_value": contract.value,
        "fee_percentage": 3.0,
        "fee_amount": fee_amount
    }