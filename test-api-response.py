import sys
sys.path.append('.')
from database import execute_query

# Get one analyzed conversation to see what fields are returned
query = """
    SELECT
        ca.id,
        ca.conversation_id,
        cl.agent_sender,
        cl.unique_id,
        cl.user_sentiment_overall,
        cl.agent_tone,
        cl.agent_energy,
        cl.agent_clarity,
        cl.agent_patience
    FROM conversation_analysis ca
    INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
    WHERE ca.review_status = 'completed'
    LIMIT 1
"""

try:
    result = execute_query(query, fetch_one=True)
    if result:
        print("Found conversation:")
        print(f"  Analysis ID: {result.get('id')}")
        print(f"  Conversation ID: {result.get('conversation_id')}")
        print(f"  Agent: {result.get('agent_sender')}")
        print(f"  Unique ID: {result.get('unique_id')}")
        print(f"  User Sentiment: {result.get('user_sentiment_overall')}")
        print(f"  Agent Tone: {result.get('agent_tone')}")
        print(f"  Agent Energy: {result.get('agent_energy')}")
        print(f"  Agent Clarity: {result.get('agent_clarity')}")
        print(f"  Agent Patience: {result.get('agent_patience')}")
    else:
        print("No completed conversations found!")

except Exception as e:
    print(f"Error: {e}")
