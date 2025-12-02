import sys
sys.path.append('.')
from database import execute_query

# Direct test of the exact query used in API
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
        crh.id as human_review_id
    FROM conversation_analysis ca
    INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
    LEFT JOIN conversation_review_human crh ON ca.id = crh.analysis_id
    WHERE ca.id = %s
"""

try:
    result = execute_query(query, ('ccc69b8c-dbe1-4ce8-8d4b-8c698a9557d1',), fetch_one=True)
    if result:
        print(f"Query returned {len(result)} keys")
        print(f"  user_sentiment_overall: {result.get('user_sentiment_overall')}")
        print(f"  agent_tone: {result.get('agent_tone')}")
        print(f"  agent_energy: {result.get('agent_energy')}")
        print(f"  agent_clarity: {result.get('agent_clarity')}")
        print(f"  agent_patience: {result.get('agent_patience')}")
    else:
        print("No result found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
