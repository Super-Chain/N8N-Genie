import requests

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