from fastapi import APIRouter, HTTPException
from typing import List
from database import execute_query
from utils import sanitize_error_message

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/list")
async def get_agents_list():
    """
    Get unique list of agents from analyzed conversations
    Used for filter dropdowns
    """
    try:
        query = """
            SELECT DISTINCT cl.agent_sender
            FROM conversations_log cl
            INNER JOIN conversation_analysis ca ON ca.conversation_id = cl.id
            WHERE cl.agent_sender IS NOT NULL
            ORDER BY cl.agent_sender
        """

        results = execute_query(query, fetch_all=True)

        agents = [str(row['agent_sender']) for row in results] if results else []

        return {"agents": agents, "total": len(agents)}

    except Exception as e:
#        print(f"Error fetching agents list: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت لیست اپراتورها: {sanitize_error_message(e)}")
