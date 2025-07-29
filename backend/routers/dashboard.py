from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List
from database.database import get_db
from database.models import Contract, RevenueTracking, PrimeContractor, ProcurementOfficer, User
from schemas.schemas import DashboardStats
from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Total and active contracts
    total_contracts = db.query(Contract).count()
    active_contracts = db.query(Contract).filter(Contract.status == "active").count()
    
    # Total revenue
    total_revenue_result = db.query(func.sum(RevenueTracking.fee_amount)).scalar()
    total_revenue = total_revenue_result if total_revenue_result else 0.0
    
    # Success rate
    total_placements = db.query(RevenueTracking).count()
    success_rate = (total_placements / total_contracts * 100) if total_contracts > 0 else 0.0
    
    # Top agencies
    top_agencies = db.query(
        Contract.agency,
        func.count(Contract.id).label('contract_count'),
        func.sum(Contract.value).label('total_value')
    ).group_by(Contract.agency).order_by(func.count(Contract.id).desc()).limit(5).all()
    
    top_agencies_list = [
        {
            "agency": agency,
            "contract_count": count,
            "total_value": total_value if total_value else 0
        }
        for agency, count, total_value in top_agencies
    ]
    
    # Monthly revenue (last 12 months)
    monthly_revenue = db.query(
        extract('year', RevenueTracking.placement_date).label('year'),
        extract('month', RevenueTracking.placement_date).label('month'),
        func.sum(RevenueTracking.fee_amount).label('revenue')
    ).group_by(
        extract('year', RevenueTracking.placement_date),
        extract('month', RevenueTracking.placement_date)
    ).order_by(
        extract('year', RevenueTracking.placement_date),
        extract('month', RevenueTracking.placement_date)
    ).limit(12).all()
    
    monthly_revenue_list = [
        {
            "year": int(year),
            "month": int(month),
            "revenue": float(revenue)
        }
        for year, month, revenue in monthly_revenue
    ]
    
    # Opportunity pipeline (contracts by opportunity score)
    opportunity_pipeline = db.query(
        Contract.opportunity_score,
        func.count(Contract.id).label('count'),
        func.sum(Contract.value).label('total_value')
    ).filter(
        Contract.opportunity_score.isnot(None),
        Contract.status == "active"
    ).group_by(Contract.opportunity_score).order_by(Contract.opportunity_score.desc()).all()
    
    opportunity_pipeline_list = [
        {
            "score": score,
            "count": count,
            "total_value": total_value if total_value else 0
        }
        for score, count, total_value in opportunity_pipeline
    ]
    
    return DashboardStats(
        total_contracts=total_contracts,
        active_contracts=active_contracts,
        total_revenue=total_revenue,
        success_rate=success_rate,
        top_agencies=top_agencies_list,
        monthly_revenue=monthly_revenue_list,
        opportunity_pipeline=opportunity_pipeline_list
    )

@router.get("/recent-activity")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Recent contracts
    recent_contracts = db.query(Contract).order_by(Contract.created_at.desc()).limit(limit).all()
    
    # Recent revenue
    recent_revenue = db.query(RevenueTracking).order_by(RevenueTracking.created_at.desc()).limit(limit).all()
    
    return {
        "recent_contracts": recent_contracts,
        "recent_revenue": recent_revenue
    }

@router.get("/performance-metrics")
def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Contract value distribution
    value_ranges = [
        {"min": 0, "max": 100000, "label": "Under $100K"},
        {"min": 100000, "max": 500000, "label": "$100K - $500K"},
        {"min": 500000, "max": 1000000, "label": "$500K - $1M"},
        {"min": 1000000, "max": 5000000, "label": "$1M - $5M"},
        {"min": 5000000, "max": None, "label": "Over $5M"}
    ]
    
    value_distribution = []
    for range_info in value_ranges:
        query = db.query(Contract).filter(Contract.value >= range_info["min"])
        if range_info["max"]:
            query = query.filter(Contract.value < range_info["max"])
        
        count = query.count()
        value_distribution.append({
            "range": range_info["label"],
            "count": count
        })
    
    # NAICS code performance
    naics_performance = db.query(
        Contract.naics_code,
        func.count(Contract.id).label('contract_count'),
        func.avg(Contract.opportunity_score).label('avg_score'),
        func.sum(Contract.value).label('total_value')
    ).group_by(Contract.naics_code).all()
    
    naics_performance_list = [
        {
            "naics_code": naics,
            "contract_count": count,
            "avg_opportunity_score": float(avg_score) if avg_score else 0,
            "total_value": float(total_value) if total_value else 0
        }
        for naics, count, avg_score, total_value in naics_performance
    ]
    
    return {
        "value_distribution": value_distribution,
        "naics_performance": naics_performance_list
    }

@router.get("/relationship-health")
def get_relationship_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Prime contractor relationship status
    contractor_status = db.query(
        PrimeContractor.relationship_status,
        func.count(PrimeContractor.id).label('count')
    ).group_by(PrimeContractor.relationship_status).all()
    
    contractor_status_list = [
        {"status": status, "count": count}
        for status, count in contractor_status
    ]
    
    # Procurement officer relationship strength
    officer_strength = db.query(
        ProcurementOfficer.relationship_strength,
        func.count(ProcurementOfficer.id).label('count')
    ).filter(ProcurementOfficer.relationship_strength.isnot(None)).group_by(
        ProcurementOfficer.relationship_strength
    ).all()
    
    officer_strength_list = [
        {"strength": strength, "count": count}
        for strength, count in officer_strength
    ]
    
    return {
        "contractor_relationships": contractor_status_list,
        "officer_relationships": officer_strength_list
    }