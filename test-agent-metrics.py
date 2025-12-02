import sys
sys.path.append('.')
from database import execute_query

# Check if columns exist
query = """
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'conversation_analysis'
AND column_name IN ('agent_tone', 'agent_energy', 'agent_clarity', 'agent_patience', 'user_sentiment_overall')
ORDER BY column_name;
"""

try:
    result = execute_query(query, fetch_all=True)
    print("Found columns in conversation_analysis:")
    for row in result:
        print(f"   - {row['column_name']}")

    if not result:
        print("No agent metrics columns found in conversation_analysis table!")
        print("\nChecking if they exist in conversations_log table...")

        query2 = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'conversations_log'
        AND column_name IN ('agent_tone', 'agent_energy', 'agent_clarity', 'agent_patience', 'user_sentiment_overall')
        ORDER BY column_name;
        """

        result2 = execute_query(query2, fetch_all=True)
        if result2:
            print("Found columns in conversations_log:")
            for row in result2:
                print(f"   - {row['column_name']}")
        else:
            print("No columns found in conversations_log either!")

except Exception as e:
    print(f"Error: {e}")
