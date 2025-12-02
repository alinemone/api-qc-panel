from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from database import execute_query

from utils import sanitize_error_message
router = APIRouter(prefix="/dashboard", tags=["Dashboard & Statistics"])


@router.get("/kpis")
async def get_dashboard_kpis(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get dashboard KPIs and statistics
    """
    try:
        # Build WHERE clauses
        where_clauses = []
        params = []
        param_counter = 1

        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = ${param_counter}")
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
                where_clauses.append(f"ca.created_at >= ${param_counter}::date AND ca.created_at < ${param_counter + 1}::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT
                -- Scores
                AVG(ca.final_percentage_score) as average_score,
                AVG(ca.conversation_score_ai) as average_conversation_score_ai,
                AVG(ca.process_score_human) as average_process_score_human,
                AVG(ca.other_criteria_score_human) as average_other_criteria_score_human,
                AVG(ca.final_score_combined) as average_final_score_combined,

                -- Counts
                COUNT(*) as total_conversations,

                -- Sentiment
                SUM(CASE WHEN ca.customer_sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_sentiment,
                SUM(CASE WHEN ca.customer_sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_sentiment,

                -- Silence metrics
                AVG(cl.silence_percentage) as average_silence_percentage,
                AVG(cl.longest_silence_gap_seconds) as average_longest_silence,
                SUM(cl.total_silence_seconds) as total_silence_seconds,

                -- Start/End sentiment
                SUM(CASE WHEN ca.customer_sentiment_start = 'positive' THEN 1 ELSE 0 END) as start_sentiment_positive,
                SUM(CASE WHEN ca.customer_sentiment_start = 'negative' THEN 1 ELSE 0 END) as start_sentiment_negative,
                SUM(CASE WHEN ca.customer_sentiment_end = 'positive' THEN 1 ELSE 0 END) as end_sentiment_positive,
                SUM(CASE WHEN ca.customer_sentiment_end = 'negative' THEN 1 ELSE 0 END) as end_sentiment_negative

            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE 1=1 {where_sql}
        """

        result = execute_query(query, tuple(params) if params else None, fetch_one=True)

        if not result:
            # Return zeros if no data
            return {
                "averageScore": 0,
                "averageConversationScoreAI": 0,
                "averageProcessScoreHuman": 0,
                "averageOtherCriteriaScoreHuman": 0,
                "averageFinalScoreCombined": 0,
                "totalConversations": 0,
                "positiveSentiment": 0,
                "negativeSentiment": 0,
                "averageSilencePercentage": 0,
                "averageLongestSilence": 0,
                "totalSilenceSeconds": 0,
                "startSentimentPositive": 0,
                "startSentimentNegative": 0,
                "endSentimentPositive": 0,
                "endSentimentNegative": 0,
                "sentimentImprovement": 0
            }

        # Calculate sentiment improvement
        start_negative = result['start_sentiment_negative'] or 0
        end_positive = result['end_sentiment_positive'] or 0
        total = result['total_conversations'] or 1  # Avoid division by zero

        sentiment_improvement = 0
        if start_negative > 0:
            sentiment_improvement = (end_positive / start_negative) * 100 if start_negative > 0 else 0

        return {
            "averageScore": float(result['average_score'] or 0),
            "averageConversationScoreAI": float(result['average_conversation_score_ai'] or 0),
            "averageProcessScoreHuman": float(result['average_process_score_human'] or 0),
            "averageOtherCriteriaScoreHuman": float(result['average_other_criteria_score_human'] or 0),
            "averageFinalScoreCombined": float(result['average_final_score_combined'] or 0),
            "totalConversations": int(result['total_conversations'] or 0),
            "positiveSentiment": int(result['positive_sentiment'] or 0),
            "negativeSentiment": int(result['negative_sentiment'] or 0),
            "averageSilencePercentage": float(result['average_silence_percentage'] or 0),
            "averageLongestSilence": float(result['average_longest_silence'] or 0),
            "totalSilenceSeconds": float(result['total_silence_seconds'] or 0),
            "startSentimentPositive": int(result['start_sentiment_positive'] or 0),
            "startSentimentNegative": int(result['start_sentiment_negative'] or 0),
            "endSentimentPositive": int(result['end_sentiment_positive'] or 0),
            "endSentimentNegative": int(result['end_sentiment_negative'] or 0),
            "sentimentImprovement": sentiment_improvement
        }

    except Exception as e:
#        print(f"Error fetching dashboard KPIs: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت آمار داشبورد: {sanitize_error_message(e)}")


@router.get("/score-trends")
async def get_score_trends(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query('last7days'),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get score trends over time (daily aggregation)
    """
    try:
        where_clauses = []
        params = []
        param_counter = 1

        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = ${param_counter}")
            params.append(agent_id)

        # Date range filter
        if date_range == 'last7days':
            where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
        elif date_range == 'last30days':
            where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
        elif date_range == 'custom' and start_date and end_date:
            where_clauses.append(f"ca.created_at >= ${param_counter}::date AND ca.created_at < ${param_counter + 1}::date + INTERVAL '1 day'")
            params.extend([start_date, end_date])

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT
                DATE(ca.created_at) as date,
                AVG(ca.final_percentage_score) as average_score,
                AVG(ca.conversation_score_ai) as average_ai_score,
                AVG(ca.final_score_combined) as average_combined_score,
                COUNT(*) as conversation_count
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE 1=1 {where_sql}
            GROUP BY DATE(ca.created_at)
            ORDER BY DATE(ca.created_at) ASC
        """

        results = execute_query(query, tuple(params) if params else None, fetch_all=True)

        return {"data": results or []}

    except Exception as e:
#        print(f"Error fetching score trends: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت روند امتیازات: {sanitize_error_message(e)}")


@router.get("/criteria-scores")
async def get_criteria_scores(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get average scores per criteria (AI scores)
    """
    try:
        where_clauses = []
        params = []
        param_counter = 1

        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = ${param_counter}")
            params.append(agent_id)

        # Date range filter
        if date_range or (start_date and end_date):
            if date_range == 'today':
                where_clauses.append("ca.created_at >= CURRENT_DATE")
            elif date_range == 'last7days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
            elif date_range == 'last30days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
            elif date_range == 'custom' and start_date and end_date:
                where_clauses.append(f"ca.created_at >= ${param_counter}::date AND ca.created_at < ${param_counter + 1}::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT
                AVG(ca.opening_score) as average_opening,
                AVG(ca.listening_score) as average_listening,
                AVG(ca.empathy_score) as average_empathy,
                AVG(ca.closing_score) as average_closing
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE 1=1 {where_sql}
        """

        result = execute_query(query, tuple(params) if params else None, fetch_one=True)

        return {
            "opening": float(result['average_opening'] or 0) if result else 0,
            "listening": float(result['average_listening'] or 0) if result else 0,
            "empathy": float(result['average_empathy'] or 0) if result else 0,
            "closing": float(result['average_closing'] or 0) if result else 0
        }

    except Exception as e:
#        print(f"Error fetching criteria scores: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت امتیازات معیارها: {sanitize_error_message(e)}")


@router.get("/human-criteria-scores")
async def get_human_criteria_scores(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get average human review scores per criteria
    """
    try:
        where_clauses = ["ca.review_status = 'review_completed'"]
        params = []
        param_counter = 1

        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = ${param_counter}")
            params.append(agent_id)

        # Date range filter
        if date_range or (start_date and end_date):
            if date_range == 'today':
                where_clauses.append("ca.created_at >= CURRENT_DATE")
            elif date_range == 'last7days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
            elif date_range == 'last30days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
            elif date_range == 'custom' and start_date and end_date:
                where_clauses.append(f"ca.created_at >= ${param_counter}::date AND ca.created_at < ${param_counter + 1}::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT
                AVG(ca.response_process_score) as average_response_process,
                AVG(ca.system_updation_score) as average_system_updation
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE {where_sql}
        """

        result = execute_query(query, tuple(params) if params else None, fetch_one=True)

        return {
            "responseProcess": float(result['average_response_process'] or 0) if result else 0,
            "systemUpdation": float(result['average_system_updation'] or 0) if result else 0
        }

    except Exception as e:
#        print(f"Error fetching human criteria scores: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت امتیازات معیارهای انسانی: {sanitize_error_message(e)}")


@router.get("/sentiment-distribution")
async def get_sentiment_distribution(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get sentiment distribution (positive/negative/neutral)
    """
    try:
        where_clauses = []
        params = []
        param_counter = 1

        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = ${param_counter}")
            params.append(agent_id)

        # Date range filter
        if date_range or (start_date and end_date):
            if date_range == 'today':
                where_clauses.append("ca.created_at >= CURRENT_DATE")
            elif date_range == 'last7days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
            elif date_range == 'last30days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
            elif date_range == 'custom' and start_date and end_date:
                where_clauses.append(f"ca.created_at >= ${param_counter}::date AND ca.created_at < ${param_counter + 1}::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT
                customer_sentiment_label,
                COUNT(*) as count
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE 1=1 {where_sql}
            GROUP BY customer_sentiment_label
        """

        results = execute_query(query, tuple(params) if params else None, fetch_all=True)

        # Convert to dict
        distribution = {row['customer_sentiment_label']: row['count'] for row in results} if results else {}

        return {
            "positive": distribution.get('positive', 0),
            "negative": distribution.get('negative', 0),
            "neutral": distribution.get('neutral', 0)
        }

    except Exception as e:
#        print(f"Error fetching sentiment distribution: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت توزیع احساسات: {sanitize_error_message(e)}")


@router.get("/top-topics")
async def get_top_topics(
    agent_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get most common conversation topics
    """
    try:
        where_clauses = []
        params = []
        param_counter = 1

        if agent_id and agent_id != 'all':
            where_clauses.append(f"cl.agent_sender = %s")
            params.append(agent_id)

        # Date range filter
        if date_range or (start_date and end_date):
            if date_range == 'today':
                where_clauses.append("ca.created_at >= CURRENT_DATE")
            elif date_range == 'last7days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '7 days'")
            elif date_range == 'last30days':
                where_clauses.append("ca.created_at >= CURRENT_DATE - INTERVAL '30 days'")
            elif date_range == 'custom' and start_date and end_date:
                where_clauses.append(f"ca.created_at >= %s::date AND ca.created_at < %s::date + INTERVAL '1 day'")
                params.extend([start_date, end_date])

        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT
                main_topic,
                COUNT(*) as count
            FROM conversation_analysis ca
            INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
            WHERE main_topic IS NOT NULL
                AND main_topic != ''
                {where_sql}
            GROUP BY main_topic
            ORDER BY COUNT(*) DESC
            LIMIT %s
        """
        params.append(limit)

        results = execute_query(query, tuple(params) if params else (limit,), fetch_all=True)

        return {"topics": results or []}

    except Exception as e:
#        print(f"Error fetching top topics: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت موضوعات پربسامد: {sanitize_error_message(e)}")
