from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from utils import sanitize_error_message
from database import execute_query

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class PaginatedResponse(BaseModel):
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/analyzed", response_model=PaginatedResponse)
async def get_analyzed_conversations(
    agent_id: Optional[str] = Query(None, description="Filter by agent extension"),
    unique_id: Optional[str] = Query(None, description="Search by call ID"),
    date_range: Optional[str] = Query(None, description="today, yesterday, last7days, last30days, custom"),
    start_date: Optional[str] = Query(None, description="Start date for custom range (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for custom range (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="pending_review or review_completed"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=10000)
):
    """
    Get analyzed conversations with filters and pagination
    """
    try:
        offset = (page - 1) * page_size

        # Build WHERE clauses
        where_clauses = []
        params = []
        param_counter = 1

        # Agent filter
        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = %s")
            params.append(agent_id)

        # Call ID search
        if unique_id and unique_id.strip():
            where_clauses.append(f"cl.unique_id ILIKE %s")
            params.append(f"%{unique_id.strip()}%")

        # Review status filter
        if status:
            where_clauses.append(f"ca.review_status = %s")
            params.append(status)

        # Date range filter
        if date_range or (start_date and end_date):
            if date_range == 'today':
                where_clauses.append(f"ca.created_at >= CURRENT_DATE")
            elif date_range == 'yesterday':
                where_clauses.append(f"ca.created_at >= CURRENT_DATE - INTERVAL '1 day' AND ca.created_at < CURRENT_DATE")
            elif date_range == 'last7days':
                where_clauses.append(f"ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
            elif date_range == 'last30days':
                where_clauses.append(f"ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
            elif date_range == 'custom' and start_date and end_date:
                where_clauses.append(f"ca.created_at >= %s::date AND ca.created_at < %s::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        # Count query
        count_query = f"""
            SELECT COUNT(*)
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE 1=1 {where_sql}
        """
        count_result = execute_query(count_query, tuple(params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        # Data query
        data_query = f"""
            SELECT
                ca.*,
                cl.conversation_data,
                cl.agent_sender,
                cl.unique_id,
                cl.total_duration_seconds,
                cl.total_silence_seconds,
                cl.longest_silence_gap_seconds,
                cl.silence_percentage,
                cl.silence_timeline,
                cl.user_sentiment_overall,
                cl.agent_tone,
                cl.agent_energy,
                cl.agent_clarity,
                cl.agent_patience,
                crh.id as human_review_id,
                crh.opening_score_override,
                crh.listening_score_override,
                crh.empathy_score_override,
                crh.response_process_score_override,
                crh.system_updation_score_override,
                crh.closing_score_override,
                crh.opening_justification_override,
                crh.listening_justification_override,
                crh.empathy_justification_override,
                crh.response_process_justification_override,
                crh.system_updation_justification_override,
                crh.closing_justification_override,
                crh.strengths_override,
                crh.areas_for_improvement_override,
                crh.total_weighted_score_human,
                crh.final_percentage_score_human,
                crh.other_criteria_weighted_score_human,
                crh.other_criteria_percentage_score_human,
                crh.reviewer_id,
                qu.full_name as reviewer_full_name,
                qu.username as reviewer_username,
                cl.created_at as created_at
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            LEFT JOIN conversation_review_human crh ON ca.id = crh.analysis_id
            LEFT JOIN qc_users qu ON crh.reviewer_id = qu.id
            WHERE 1=1 {where_sql}
            ORDER BY cl.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])

        data = execute_query(data_query, tuple(params), fetch_all=True)

        total_pages = (total + page_size - 1) // page_size

        return {
            "data": data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except Exception as e:
#        print(f"Error fetching analyzed conversations: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت مکالمات تحلیل شده: {sanitize_error_message(e)}")


@router.get("/analyzed/{analysis_id}")
async def get_analyzed_conversation_by_id(analysis_id: str):
    """
    Get single analyzed conversation with all details
    """
    try:
        query = """
            SELECT
                ca.*,
                cl.conversation_data,
                cl.agent_sender,
                cl.unique_id,
                cl.total_duration_seconds,
                cl.total_silence_seconds,
                cl.longest_silence_gap_seconds,
                cl.silence_percentage,
                cl.silence_timeline,
                cl.user_sentiment_overall,
                cl.agent_tone,
                cl.agent_energy,
                cl.agent_clarity,
                cl.agent_patience,
                crh.id as human_review_id,
                crh.opening_score_override,
                crh.listening_score_override,
                crh.empathy_score_override,
                crh.response_process_score_override,
                crh.system_updation_score_override,
                crh.closing_score_override,
                crh.opening_justification_override,
                crh.listening_justification_override,
                crh.empathy_justification_override,
                crh.response_process_justification_override,
                crh.system_updation_justification_override,
                crh.closing_justification_override,
                crh.strengths_override,
                crh.areas_for_improvement_override,
                crh.total_weighted_score_human,
                crh.final_percentage_score_human,
                crh.other_criteria_weighted_score_human,
                crh.other_criteria_percentage_score_human,
                crh.reviewer_id,
                qu.full_name as reviewer_full_name,
                qu.username as reviewer_username,
                cl.created_at as created_at
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            LEFT JOIN conversation_review_human crh ON ca.id = crh.analysis_id
            LEFT JOIN qc_users qu ON crh.reviewer_id = qu.id
            WHERE ca.id = %s
        """

        result = execute_query(query, (analysis_id,), fetch_one=True)

        if not result:
            raise HTTPException(status_code=404, detail="مکالمه یافت نشد")

        return result

    except HTTPException:
        raise
    except Exception as e:
#        print(f"Error fetching conversation by ID: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت مکالمه: {sanitize_error_message(e)}")


@router.get("/unanalyzed", response_model=PaginatedResponse)
async def get_unanalyzed_conversations(
    agent_id: Optional[str] = Query(None),
    unique_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=10000)
):
    """
    Get conversations that haven't been analyzed yet
    """
    try:
        offset = (page - 1) * page_size

        # Build WHERE clauses
        where_clauses = ["is_analyzed = false"]
        params = []

        if agent_id and agent_id != 'all':
            where_clauses.append(f"agent_sender = %s")
            params.append(agent_id)

        if unique_id and unique_id.strip():
            where_clauses.append(f"unique_id ILIKE %s")
            params.append(f"%{unique_id.strip()}%")

        where_sql = " AND ".join(where_clauses)

        # Count query
        count_query = f"SELECT COUNT(*) FROM conversations_log WHERE {where_sql}"
        count_result = execute_query(count_query, tuple(params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        # Data query
        data_query = f"""
            SELECT id, created_at, unique_id, is_analyzed, agent_sender
            FROM conversations_log
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])

        data = execute_query(data_query, tuple(params), fetch_all=True)

        total_pages = (total + page_size - 1) // page_size

        return {
            "data": data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except Exception as e:
#        print(f"Error fetching unanalyzed conversations: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت مکالمات تحلیل نشده: {sanitize_error_message(e)}")


@router.post("/analyze/batch")
async def trigger_batch_analysis(unique_ids: List[str]):
    """
    Trigger AI analysis for multiple conversations via n8n webhook
    Note: This is a placeholder - actual n8n triggering should be implemented
    """
    try:
        # TODO: Implement n8n webhook calls
        # For each unique_id, call: https://n8n.basalam.dev/webhook/analysis?unique_id={unique_id}

        return {
            "message": f"{len(unique_ids)} مکالمه برای تحلیل ارسال شد",
            "unique_ids": unique_ids,
            "note": "این قابلیت نیاز به پیاده‌سازی فراخوانی webhook دارد"
        }

    except Exception as e:
#        print(f"Error triggering batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در ارسال برای تحلیل: {sanitize_error_message(e)}")
