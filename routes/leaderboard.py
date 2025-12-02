from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import execute_query

from utils import sanitize_error_message
router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/agents")
async def get_agent_leaderboard(
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get agent performance rankings
    """
    try:
        # Build WHERE clauses for date filtering
        where_clauses = []
        params = []
        param_counter = 1

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
                where_clauses.append(f"ca.created_at >= ${param_counter}::date AND ca.created_at < ${param_counter + 1}::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])
                param_counter += 2

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT
                cl.agent_sender as agent_extension,
                COUNT(*) as total_conversations,
                AVG(ca.final_percentage_score) as average_score,
                AVG(ca.opening_score) as average_opening_score,
                AVG(ca.listening_score) as average_listening_score,
                AVG(ca.empathy_score) as average_empathy_score,
                AVG(ca.response_process_score) as average_response_score,
                AVG(ca.closing_score) as average_closing_score,
                AVG(cl.silence_percentage) as average_silence_percent,

                -- Sentiment improvement calculation
                CASE
                    WHEN SUM(CASE WHEN ca.customer_sentiment_start = 'negative' THEN 1 ELSE 0 END) > 0
                    THEN (
                        SUM(CASE WHEN ca.customer_sentiment_end = 'positive' THEN 1 ELSE 0 END)::float /
                        SUM(CASE WHEN ca.customer_sentiment_start = 'negative' THEN 1 ELSE 0 END)::float
                    ) * 100
                    ELSE 0
                END as sentiment_improvement_percent

            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE cl.agent_sender IS NOT NULL
                
                
                {where_sql}
            GROUP BY cl.agent_sender
            HAVING COUNT(*) > 0
            ORDER BY AVG(ca.final_percentage_score) DESC
        """

        results = execute_query(query, tuple(params) if params else None, fetch_all=True)

        # Add rank to results
        leaderboard = []
        for rank, row in enumerate(results or [], start=1):
            leaderboard.append({
                "rank": rank,
                "agentExtension": row['agent_extension'],
                "totalConversations": int(row['total_conversations'] or 0),
                "averageScore": float(row['average_score'] or 0),
                "averageOpeningScore": float(row['average_opening_score'] or 0),
                "averageListeningScore": float(row['average_listening_score'] or 0),
                "averageEmpathyScore": float(row['average_empathy_score'] or 0),
                "averageResponseScore": float(row['average_response_score'] or 0),
                "averageClosingScore": float(row['average_closing_score'] or 0),
                "sentimentImprovementPercent": float(row['sentiment_improvement_percent'] or 0),
                "averageSilencePercent": float(row['average_silence_percent'] or 0)
            })

        return {"leaderboard": leaderboard, "total": len(leaderboard)}

    except Exception as e:
#        print(f"Error fetching agent leaderboard: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت جدول رتبه‌بندی: {sanitize_error_message(e)}")
