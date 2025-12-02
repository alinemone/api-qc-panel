import sys
sys.path.append('.')
from database import execute_query

# Check review status
unique_id = '1764574625.5423567'

query = """
    SELECT
        ca.id as analysis_id,
        ca.review_status,
        cl.qc_status,
        cl.unique_id
    FROM conversation_analysis ca
    INNER JOIN conversations_log cl ON ca.conversation_id = cl.id
    WHERE cl.unique_id = %s
"""

try:
    result = execute_query(query, (unique_id,), fetch_one=True)
    if result:
        print(f"Unique ID: {result.get('unique_id')}")
        print(f"Analysis ID: {result.get('analysis_id')}")
        print(f"Review Status (conversation_analysis): {result.get('review_status')}")
        print(f"QC Status (conversations_log): {result.get('qc_status')}")
    else:
        print(f"No conversation found with unique_id: {unique_id}")

except Exception as e:
    print(f"Error: {e}")
