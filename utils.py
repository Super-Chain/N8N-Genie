import requests
from datetime import datetime, timedelta
from collections import defaultdict
import threading

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FastAPI')

def get_node_types():
    url = 'https://raw.githubusercontent.com/n8n-io/n8n/refs/heads/master/packages/frontend/editor-ui/src/constants.ts'

    response = requests.get(url)

    lines = response.text.split('\n')

    node_types = [line for line in lines if "NODE_TYPE = '" in line]

    node_types = [line.split("NODE_TYPE = '")[1].split("';")[0] for line in node_types]

    return node_types

def clear_workflow(workflow):
    workflow['nodes'] = [
        node for node in workflow['nodes'] 
        if node['type'] != 'n8n-nodes-base.stickyNote'
    ]

    workflow.pop('createdAt', None)
    workflow.pop('updatedAt', None)

    return workflow


# API call tracking storage
api_call_tracker = defaultdict(lambda: defaultdict(int))
tracker_lock = threading.Lock()

def check_and_store_api_call(email: str, daily_limit: int = 5) -> bool:
    """
    Check if user has exceeded daily API call limit and store the call.
    
    Args:
        email (str): User email
        daily_limit (int): Maximum API calls allowed per day (default: 5)
    
    Returns:
        bool: True if call is allowed, False if limit exceeded
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    with tracker_lock:
        # Clean up old entries (older than 2 days)
        cutoff_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        users_to_clean = []
        for tracked_user in list(api_call_tracker.keys()):
            dates_to_clean = []
            for date in list(api_call_tracker[tracked_user].keys()):
                if date < cutoff_date:
                    dates_to_clean.append(date)
            
            for date in dates_to_clean:
                del api_call_tracker[tracked_user][date]
            
            if not api_call_tracker[tracked_user]:
                users_to_clean.append(tracked_user)
        
        for tracked_user in users_to_clean:
            del api_call_tracker[tracked_user]
        
        # Check current user's daily limit
        current_calls = api_call_tracker[email][today]
        
        if current_calls >= daily_limit:
            logger.warning(f"User {email} exceeded daily API limit ({current_calls}/{daily_limit})")
            return False
        
        # Increment the call count
        api_call_tracker[email][today] += 1
        logger.info(f"User {email} API call count for {today}: {api_call_tracker[email][today]}/{daily_limit}")
        
        return True