from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict
from database import execute_query
from utils import sanitize_error_message

router = APIRouter(prefix="/settings", tags=["QC Settings"])


class WeightsUpdate(BaseModel):
    opening: float
    listening: float
    empathy: float
    response_process: float
    system_updation: float
    closing: float
    updated_by: str


@router.get("/weights")
async def get_current_weights():
    """
    Get current QC weights from qc_settings
    """
    try:
        query = """
            SELECT setting_value
            FROM qc_settings
            WHERE setting_key = 'weights'
        """

        result = execute_query(query, fetch_one=True)

        if not result:
            # Return default weights if not found
            return {
                "opening": 2,
                "listening": 12,
                "empathy": 10,
                "response_process": 15,
                "system_updation": 12,
                "closing": 4
            }

        # Convert camelCase from database to snake_case
        db_weights = result['setting_value']
        return {
            "opening": db_weights.get('opening', 2),
            "listening": db_weights.get('listening', 12),
            "empathy": db_weights.get('empathy', 10),
            "response_process": db_weights.get('responseProcess', 15),
            "system_updation": db_weights.get('systemUpdation', 12),
            "closing": db_weights.get('closing', 4)
        }

    except Exception as e:
#        print(f"Error fetching weights: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت وزن‌ها: {sanitize_error_message(e)}")


@router.put("/weights")
async def update_weights(weights: WeightsUpdate):
    """
    Update QC weights (Admin only)
    """
    try:
        # Convert snake_case to camelCase for database storage
        db_weights = {
            "opening": weights.opening,
            "listening": weights.listening,
            "empathy": weights.empathy,
            "responseProcess": weights.response_process,
            "systemUpdation": weights.system_updation,
            "closing": weights.closing
        }

        # Use PostgreSQL JSON type for setting_value
        query = """
            UPDATE qc_settings
            SET
                setting_value = %s::jsonb,
                updated_at = NOW(),
                updated_by = %s
            WHERE setting_key = 'weights'
        """

        import json
        execute_query(query, (json.dumps(db_weights), weights.updated_by), fetch_all=False)

        return {"message": "وزن‌ها با موفقیت به‌روزرسانی شد", "weights": db_weights}

    except Exception as e:
#        print(f"Error updating weights: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در به‌روزرسانی وزن‌ها: {sanitize_error_message(e)}")


@router.get("/max-score")
async def get_max_score():
    """
    Get max score per metric from qc_settings
    """
    try:
        query = """
            SELECT setting_value
            FROM qc_settings
            WHERE setting_key = 'max_score_per_metric'
        """

        result = execute_query(query, fetch_one=True)

        if not result:
            return {"max_score_per_metric": 4}

        return {"max_score_per_metric": result['setting_value']}

    except Exception as e:
#        print(f"Error fetching max score: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت حداکثر امتیاز: {sanitize_error_message(e)}")
