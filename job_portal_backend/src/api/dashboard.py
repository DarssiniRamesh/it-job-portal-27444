from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from .db import get_db
from .auth import require_any_role
from .models import User, RoleEnum, Job, Application
from .schemas import Role

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "/dashboard/employer",
    summary="Employer Dashboard Stats",
    description="Aggregate dashboard data for employer users about their job postings and applicant statistics.",
    tags=["Dashboard"],
    responses={200: {"description": "Employer dashboard data."}},
)
def employer_dashboard(
    current_user: User = Depends(require_any_role(Role.employer, Role.admin)),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return dashboard statistics for employers (jobs posted, applicants, stats)."""
    if current_user.role not in [RoleEnum.employer, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not an employer or admin.")

    # Total jobs posted by employer
    jobs = db.query(Job).filter(Job.employer_id == current_user.id).all()
    job_ids = [job.id for job in jobs]
    total_jobs = len(jobs)

    # Total applications received for all jobs
    total_applications = db.query(func.count(Application.id)).filter(Application.job_id.in_(job_ids)).scalar() if job_ids else 0

    # Applications status breakdown
    status_counts = dict(
        db.query(Application.status, func.count(Application.id))
        .filter(Application.job_id.in_(job_ids))
        .group_by(Application.status)
        .all()
    ) if job_ids else {}

    # Turn status enum keys into string for JSON response
    status_counts_str = {str(k): v for k, v in status_counts.items()}

    return {
        "employer_id": current_user.id,
        "total_jobs_posted": total_jobs,
        "total_applications_received": total_applications,
        "application_statuses": status_counts_str,
    }


# PUBLIC_INTERFACE
@router.get(
    "/dashboard/job_seeker",
    summary="Job Seeker Dashboard Stats",
    description="Aggregate dashboard data for job seeker users about their applications and statuses.",
    tags=["Dashboard"],
    responses={200: {"description": "Job seeker dashboard data."}},
)
def job_seeker_dashboard(
    current_user: User = Depends(require_any_role(Role.job_seeker, Role.admin)),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return dashboard statistics for job seekers (applications submitted, status breakdown, recent activity)."""
    if current_user.role not in [RoleEnum.job_seeker, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not a job seeker or admin.")

    # Total applications submitted
    total_applied = db.query(func.count(Application.id)).filter(Application.user_id == current_user.id).scalar()

    # Applications breakdown by status
    status_breakdown_query = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.user_id == current_user.id)
        .group_by(Application.status)
        .all()
    )
    status_breakdown = {str(status): count for status, count in status_breakdown_query}

    # Recent applications (last 5), by submission time descending
    recent_apps = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .limit(5)
        .all()
    )
    recent_apps_resp = [
        {
            "application_id": app.id,
            "job_id": app.job_id,
            "submitted_at": app.created_at,
            "status": str(app.status),
        }
        for app in recent_apps
    ]

    return {
        "job_seeker_id": current_user.id,
        "total_applications": total_applied,
        "application_statuses": status_breakdown,
        "recent_applications": recent_apps_resp,
    }
