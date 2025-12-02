from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from database import execute_query

from utils import sanitize_error_message
router = APIRouter(prefix="/comparison", tags=["AI vs Human Comparison"])


@router.get("/reviewed-conversations")
async def get_reviewed_conversations(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500)
):
    """
    Get all reviewed conversations for AI vs Human comparison
    """
    try:
        offset = (page - 1) * page_size

        # Build WHERE clauses
        where_clauses = [
            "ca.review_status = 'completed'",
            "cl.qc_status = 'completed'"
        ]
        params = []

        if agent_id and agent_id != 'all':
            where_clauses.append("cl.agent_sender = %s")
            params.append(agent_id)

        # Date range filter
        if date_range or (start_date and end_date):
            if date_range == 'today':
                where_clauses.append("ca.created_at >= CURRENT_DATE")
            elif date_range == 'yesterday':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '1 day' AND ca.created_at < CURRENT_DATE")
            elif date_range == 'last7days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
            elif date_range == 'last30days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
            elif date_range == 'custom' and start_date and end_date:
                where_clauses.append("ca.created_at >= %s::date AND ca.created_at < %s::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND ".join(where_clauses)

        # Count query
        count_query = f"""
            SELECT COUNT(*)
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE {where_sql}
        """
        count_result = execute_query(count_query, tuple(params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        # Data query
        query = f"""
            SELECT
                ca.id,
                ca.created_at,
                ca.opening_score,
                ca.listening_score,
                ca.empathy_score,
                ca.response_process_score,
                ca.system_updation_score,
                ca.closing_score,
                ca.total_weighted_score,
                ca.final_percentage_score,
                ca.conversation_score_ai,
                ca.process_score_human,
                ca.other_criteria_score_human,
                ca.final_score_combined,
                cl.agent_sender,
                cl.unique_id,
                crh.opening_score_override,
                crh.listening_score_override,
                crh.empathy_score_override,
                crh.response_process_score_override,
                crh.system_updation_score_override,
                crh.closing_score_override,
                crh.total_weighted_score_human,
                crh.final_percentage_score_human,
                crh.other_criteria_weighted_score_human,
                crh.other_criteria_percentage_score_human,
                crh.reviewer_id,
                qu.full_name as reviewer_full_name,
                qu.username as reviewer_username
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            LEFT JOIN conversation_review_human crh ON ca.id = crh.analysis_id
            LEFT JOIN qc_users qu ON crh.reviewer_id = qu.id
            WHERE {where_sql}
            ORDER BY ca.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])

        data = execute_query(query, tuple(params), fetch_all=True)

        total_pages = (total + page_size - 1) // page_size

        return {
            "data": data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except Exception as e:
#        print(f"Error fetching reviewed conversations: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت مکالمات بررسی شده: {sanitize_error_message(e)}")


@router.get("/conversation/{analysis_id}")
async def get_conversation_comparison(analysis_id: str):
    """
    Get detailed AI vs Human comparison for a single conversation
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

        # Calculate score differences
        if result.get('human_review_id'):
            result['score_differences'] = {
                'opening': (result.get('opening_score_override') or 0) - (result.get('opening_score') or 0),
                'listening': (result.get('listening_score_override') or 0) - (result.get('listening_score') or 0),
                'empathy': (result.get('empathy_score_override') or 0) - (result.get('empathy_score') or 0),
                'response_process': (result.get('response_process_score_override') or 0) - (result.get('response_process_score') or 0),
                'system_updation': (result.get('system_updation_score_override') or 0) - (result.get('system_updation_score') or 0),
                'closing': (result.get('closing_score_override') or 0) - (result.get('closing_score') or 0),
            }

        return result

    except HTTPException:
        raise
    except Exception as e:
#        print(f"Error fetching conversation comparison: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت مقایسه: {sanitize_error_message(e)}")
