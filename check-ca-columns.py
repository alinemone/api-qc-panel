import sys
sys.path.append('.')
from database import execute_query

# Check if conversation_analysis table has these columns
query = """
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'conversation_analysis'
AND column_name IN ('user_sentiment_overall', 'agent_tone', 'agent_energy', 'agent_clarity', 'agent_patience')
ORDER BY column_name;
"""

try:
    result = execute_query(query, fetch_all=True)
    if result:
        print("Found columns in conversation_analysis:")
        for row in result:
            print(f"   - {row['column_name']}")
    else:
        print("No agent metrics columns found in conversation_analysis table")

except Exception as e:
    print(f"Error: {e}")
