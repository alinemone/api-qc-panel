from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import execute_query
from utils import sanitize_error_message
import json
from psycopg2.extras import Json

router = APIRouter(prefix="/reviews", tags=["QC Reviews"])


class ReviewSubmission(BaseModel):
    analysis_id: str
    reviewer_id: str
    opening_score_override: Optional[float] = None
    listening_score_override: Optional[float] = None
    empathy_score_override: Optional[float] = None
    response_process_score_override: Optional[float] = None
    system_updation_score_override: Optional[float] = None
    closing_score_override: Optional[float] = None
    opening_justification_override: Optional[str] = None
    listening_justification_override: Optional[str] = None
    empathy_justification_override: Optional[str] = None
    response_process_justification_override: Optional[str] = None
    system_updation_justification_override: Optional[str] = None
    closing_justification_override: Optional[str] = None
    strengths_override: Optional[str] = None
    areas_for_improvement_override: Optional[str] = None
    total_weighted_score_human: float
    final_percentage_score_human: float
    other_criteria_weighted_score_human: float
    other_criteria_percentage_score_human: float


@router.get("/pending")
async def get_pending_reviews(
    agent_id: Optional[str] = Query(None, description="Filter by agent extension")
):
    """
    Get conversations pending QC review
    """
    try:
        where_clause = "ca.review_status = 'pending_review'"
        params = []

        if agent_id and agent_id != 'all':
            where_clause += " AND cl.agent_sender = %s"
            params.append(agent_id)

        query = f"""
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
                cl.created_at as created_at
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE {where_clause}
            ORDER BY cl.created_at ASC
        """

        data = execute_query(query, tuple(params) if params else None, fetch_all=True)

        return {"data": data or [], "total": len(data or [])}

    except Exception as e:
#        print(f"Error fetching pending reviews: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت بررسی‌های در انتظار: {sanitize_error_message(e)}")


@router.get("/completed")
async def get_completed_reviews(
    agent_id: Optional[str] = Query(None, description="Filter by agent extension")
):
    """
    Get completed QC reviews
    """
    try:
        where_clause = "ca.review_status = 'review_completed'"
        params = []

        if agent_id and agent_id != 'all':
            where_clause += " AND cl.agent_sender = %s"
            params.append(agent_id)

        query = f"""
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
            WHERE {where_clause}
            ORDER BY cl.created_at DESC
        """

        data = execute_query(query, tuple(params) if params else None, fetch_all=True)

        return {"data": data or [], "total": len(data or [])}

    except Exception as e:
#        print(f"Error fetching completed reviews: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت بررسی‌های تکمیل شده: {sanitize_error_message(e)}")


@router.get("/analysis/{analysis_id}")
async def get_review_by_analysis_id(analysis_id: str):
    """
    Get existing human review for an analysis
    """
    try:
        query = """
            SELECT crh.*, qu.full_name as reviewer_full_name, qu.username as reviewer_username
            FROM conversation_review_human crh
            LEFT JOIN qc_users qu ON crh.reviewer_id = qu.id
            WHERE crh.analysis_id = %s
        """

        result = execute_query(query, (analysis_id,), fetch_one=True)

        return result if result else None

    except Exception as e:
#        print(f"Error fetching review: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت بررسی: {sanitize_error_message(e)}")


@router.post("/submit")
async def submit_review(review: ReviewSubmission):
    """
    Submit or update a human QC review
    """
    try:
        # Check if review already exists
        check_query = "SELECT id FROM conversation_review_human WHERE analysis_id = %s"
        existing = execute_query(check_query, (review.analysis_id,), fetch_one=True)

        if existing:
            # UPDATE existing review
            update_query = """
                UPDATE conversation_review_human
                SET
                    reviewer_id = %s,
                    opening_score_override = %s,
                    listening_score_override = %s,
                    empathy_score_override = %s,
                    response_process_score_override = %s,
                    system_updation_score_override = %s,
                    closing_score_override = %s,
                    opening_justification_override = %s,
                    listening_justification_override = %s,
                    empathy_justification_override = %s,
                    response_process_justification_override = %s,
                    system_updation_justification_override = %s,
                    closing_justification_override = %s,
                    strengths_override = %s,
                    areas_for_improvement_override = %s,
                    total_weighted_score_human = %s,
                    final_percentage_score_human = %s,
                    other_criteria_weighted_score_human = %s,
                    other_criteria_percentage_score_human = %s
                WHERE analysis_id = %s
            """

            execute_query(update_query, (
                review.reviewer_id,
                review.opening_score_override,
                review.listening_score_override,
                review.empathy_score_override,
                review.response_process_score_override,
                review.system_updation_score_override,
                review.closing_score_override,
                review.opening_justification_override,
                review.listening_justification_override,
                review.empathy_justification_override,
                review.response_process_justification_override,
                review.system_updation_justification_override,
                review.closing_justification_override,
                review.strengths_override,
                review.areas_for_improvement_override,
                review.total_weighted_score_human,
                review.final_percentage_score_human,
                review.other_criteria_weighted_score_human,
                review.other_criteria_percentage_score_human,
                review.analysis_id
            ), fetch_all=False)

        else:
            # INSERT new review - must get weights_snapshot from original analysis
            import sys
            sys.stdout.write(f"[DEBUG] Starting INSERT path for analysis_id: {review.analysis_id}\n")
            sys.stdout.flush()

            analysis_query = "SELECT weights_snapshot FROM conversation_analysis WHERE id = %s"
            sys.stdout.write(f"[DEBUG] About to execute analysis_query\n")
            sys.stdout.flush()
            analysis_data = execute_query(analysis_query, (review.analysis_id,), fetch_one=True)
            sys.stdout.write(f"[DEBUG] Executed analysis_query successfully\n")
            sys.stdout.flush()

            if not analysis_data or not analysis_data.get('weights_snapshot'):
                raise HTTPException(status_code=404, detail="تحلیل یافت نشد یا weights_snapshot موجود نیست")

            weights_snapshot = analysis_data['weights_snapshot']
            sys.stdout.write(f"[DEBUG] weights_snapshot type: {type(weights_snapshot)}\n")
            sys.stdout.write(f"[DEBUG] weights_snapshot value: {weights_snapshot}\n")
            sys.stdout.flush()

            # Get max score per metric from settings
            max_score_query = """
                SELECT setting_value FROM qc_settings WHERE setting_key = 'max_score_per_metric'
            """
            sys.stdout.write(f"[DEBUG] About to execute max_score_query\n")
            sys.stdout.flush()
            max_score_result = execute_query(max_score_query, fetch_one=True)
            sys.stdout.write(f"[DEBUG] Executed max_score_query successfully\n")
            sys.stdout.flush()
            max_score_per_metric = max_score_result['setting_value'] if max_score_result else 4

            # Calculate max_possible_overall_score (ALL 6 criteria)
            weights = weights_snapshot
            max_possible_overall_score = max_score_per_metric * (
                weights.get('opening', 2) +
                weights.get('listening', 12) +
                weights.get('empathy', 10) +
                weights.get('response_process', 15) +
                weights.get('system_updation', 12) +
                weights.get('closing', 4)
            )

            # Use psycopg2 Json adapter for JSONB field
            print(f"[DEBUG] weights_snapshot before Json(): {weights_snapshot}")

            insert_query = """
                INSERT INTO conversation_review_human (
                    analysis_id,
                    reviewer_id,
                    opening_score_override,
                    listening_score_override,
                    empathy_score_override,
                    response_process_score_override,
                    system_updation_score_override,
                    closing_score_override,
                    opening_justification_override,
                    listening_justification_override,
                    empathy_justification_override,
                    response_process_justification_override,
                    system_updation_justification_override,
                    closing_justification_override,
                    strengths_override,
                    areas_for_improvement_override,
                    total_weighted_score_human,
                    final_percentage_score_human,
                    other_criteria_weighted_score_human,
                    other_criteria_percentage_score_human,
                    weights_snapshot,
                    max_possible_overall_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            execute_query(insert_query, (
                review.analysis_id,
                review.reviewer_id,
                review.opening_score_override,
                review.listening_score_override,
                review.empathy_score_override,
                review.response_process_score_override,
                review.system_updation_score_override,
                review.closing_score_override,
                review.opening_justification_override,
                review.listening_justification_override,
                review.empathy_justification_override,
                review.response_process_justification_override,
                review.system_updation_justification_override,
                review.closing_justification_override,
                review.strengths_override,
                review.areas_for_improvement_override,
                review.total_weighted_score_human,
                review.final_percentage_score_human,
                review.other_criteria_weighted_score_human,
                review.other_criteria_percentage_score_human,
                Json(weights_snapshot),  # Use psycopg2 Json adapter
                max_possible_overall_score
            ), fetch_all=False)

        # Update analysis status to completed
        status_update = """
            UPDATE conversation_analysis
            SET review_status = 'completed'
            WHERE id = %s
        """
        execute_query(status_update, (review.analysis_id,), fetch_all=False)

        # Update qc_status in conversations_log to 'completed'
        qc_status_update = """
            UPDATE conversations_log
            SET qc_status = 'completed'
            WHERE id = (
                SELECT conversation_id
                FROM conversation_analysis
                WHERE id = %s
            )
        """
        execute_query(qc_status_update, (review.analysis_id,), fetch_all=False)

        return {"message": "بررسی با موفقیت ثبت شد"}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import sys
        error_traceback = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Full traceback:\n{error_traceback}\n")
        sys.stderr.flush()
#        print(f"Error submitting review: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در ثبت بررسی: {sanitize_error_message(e)}")
