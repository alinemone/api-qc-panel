import sys
sys.path.append('.')
from database import execute_query

# Check specific unique_id
unique_id = '1764574625.5423567'

query = """
    SELECT
        ca.id as analysis_id,
        ca.conversation_id,
        cl.id as log_id,
        cl.unique_id,
        cl.agent_sender,
        cl.user_sentiment_overall,
        cl.agent_tone,
        cl.agent_energy,
        cl.agent_clarity,
        cl.agent_patience
    FROM conversation_analysis ca
    INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
    WHERE cl.unique_id = %s
"""

try:
    result = execute_query(query, (unique_id,), fetch_one=True)
    if result:
        print(f"Found conversation with unique_id: {unique_id}")
        print(f"  Analysis ID: {result.get('analysis_id')}")
        print(f"  Conversation ID: {result.get('conversation_id')}")
        print(f"  Log ID: {result.get('log_id')}")
        print(f"  Agent: {result.get('agent_sender')}")
        print(f"  User Sentiment: '{result.get('user_sentiment_overall')}'")
        print(f"  Agent Tone: '{result.get('agent_tone')}'")
        print(f"  Agent Energy: '{result.get('agent_energy')}'")
        print(f"  Agent Clarity: '{result.get('agent_clarity')}'")
        print(f"  Agent Patience: '{result.get('agent_patience')}'")

        # Also check directly from conversations_log
        print("\n--- Direct check from conversations_log ---")
        direct_query = """
            SELECT
                id,
                unique_id,
                user_sentiment_overall,
                agent_tone,
                agent_energy,
                agent_clarity,
                agent_patience
            FROM conversations_log
            WHERE unique_id = %s
        """
        direct_result = execute_query(direct_query, (unique_id,), fetch_one=True)
        if direct_result:
            print(f"  ID: {direct_result.get('id')}")
            print(f"  Unique ID: {direct_result.get('unique_id')}")
            print(f"  User Sentiment: '{direct_result.get('user_sentiment_overall')}'")
            print(f"  Agent Tone: '{direct_result.get('agent_tone')}'")
            print(f"  Agent Energy: '{direct_result.get('agent_energy')}'")
            print(f"  Agent Clarity: '{direct_result.get('agent_clarity')}'")
            print(f"  Agent Patience: '{direct_result.get('agent_patience')}'")
    else:
        print(f"No conversation found with unique_id: {unique_id}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
