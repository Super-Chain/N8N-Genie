from utils import get_node_types

SYSTEM_PROMPT = r"""You are a helpful assistant that can generate n8n workflow json based on the user's query. 

Here is the few shot example for workflow json.
```
{
  "createdAt": "2025-03-11T17:52:12.078Z",
  "updatedAt": "2025-03-11T17:56:05.000Z",
  "id": "258",
  "name": "Agent:auto-fix:openai",
  "active": false,
  "nodes": [
    {
      "parameters": {},
      "id": "9152fa2f-1cf1-4745-bf52-3d3374e501c5",
      "name": "When clicking \"Test workflow\"",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [
        160,
        820
      ]
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "What time is my check-in?",
        "hasOutputParser": true,
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.8,
      "position": [
        480,
        820
      ],
      "id": "1c390448-79da-4a49-b7f2-3a7a99a23167",
      "name": "AI Agent"
    },
    {
      "parameters": {
        "model": {
          "__rl": true,
          "value": "gpt-4o-2024-05-13",
          "mode": "list",
          "cachedResultName": "gpt-4o-2024-05-13"
        },
        "options": {
          "temperature": 0,
          "maxRetries": 3
        }
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1.2,
      "position": [
        240,
        1100
      ],
      "id": "71ffd19c-f0eb-4735-bdd5-4c8e9511fcc2",
      "name": "OpenAI Chat Model",
      "credentials": {
        "openAiApi": {
          "id": "Zak03cqeLUOsgkFI",
          "name": "OpenAi account"
        }
      }
    },
    {
      "parameters": {
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.outputParserAutofixing",
      "typeVersion": 1,
      "position": [
        720,
        1100
      ],
      "id": "72cafb7e-889c-46cf-bfe1-ac71e9803037",
      "name": "Auto-fixing Output Parser"
    },
    {
      "parameters": {
        "schemaType": "manual",
        "inputSchema": "{\n  \"type\": \"object\",\n  \"properties\": {\n    \"resolution\": {\n      \"type\": \"string\",\n      \"description\": \"The customer-facing resolution or response that should be communicated to the customer\"\n    },\n    \"reasoning\": {\n      \"type\": \"string\",\n      \"description\": \"Detailed explanation of the solution and reasoning for internal use\"\n    }\n  },\n  \"additionalProperties\": true,\n  \"required\": [\"resolution\", \"reasoning\"]\n}"
      },
      "type": "@n8n/n8n-nodes-langchain.outputParserStructured",
      "typeVersion": 1.2,
      "position": [
        860,
        1240
      ],
      "id": "58ab5ac8-9f75-4448-a4c9-55a8d2afa8fd",
      "name": "Structured Output Parser"
    },
    {
      "parameters": {
        "sessionIdType": "customKey",
        "sessionKey": "memory6"
      },
      "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      "typeVersion": 1.3,
      "position": [
        500,
        1100
      ],
      "id": "af4542a6-23e2-4baf-8544-b01aa16d22aa",
      "name": "Simple Memory"
    },
    {
      "parameters": {
        "model": {
          "__rl": true,
          "mode": "list",
          "value": "gpt-4o-mini"
        },
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1.2,
      "position": [
        660,
        1240
      ],
      "id": "84ebbc2c-ed7f-418b-b4b0-e0f273912d79",
      "name": "OpenAI Chat Model1",
      "credentials": {
        "openAiApi": {
          "id": "Zak03cqeLUOsgkFI",
          "name": "OpenAi account"
        }
      }
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "What time is my check-in?",
        "hasOutputParser": true,
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.8,
      "position": [
        880,
        820
      ],
      "id": "92c04ad7-f491-4f0f-86de-c32fe82c2148",
      "name": "AI Agent1"
    },
    {
      "parameters": {
        "content": "## Auto-fixing Output Parser + Memory\n",
        "height": 88,
        "width": 386
      },
      "id": "38f59837-adec-49dc-b848-0b97561c3842",
      "name": "Sticky Note4",
      "type": "n8n-nodes-base.stickyNote",
      "typeVersion": 1,
      "position": [
        320,
        700
      ]
    }
  ],
  "connections": {
    "When clicking \"Test workflow\"": {
      "main": [
        [
          {
            "node": "AI Agent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Auto-fixing Output Parser": {
      "ai_outputParser": [
        [
          {
            "node": "AI Agent",
            "type": "ai_outputParser",
            "index": 0
          },
          {
            "node": "AI Agent1",
            "type": "ai_outputParser",
            "index": 0
          }
        ]
      ]
    },
    "Structured Output Parser": {
      "ai_outputParser": [
        [
          {
            "node": "Auto-fixing Output Parser",
            "type": "ai_outputParser",
            "index": 0
          }
        ]
      ]
    },
    "Simple Memory": {
      "ai_memory": [
        [
          {
            "node": "AI Agent",
            "type": "ai_memory",
            "index": 0
          },
          {
            "node": "AI Agent1",
            "type": "ai_memory",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI Chat Model1": {
      "ai_languageModel": [
        [
          {
            "node": "Auto-fixing Output Parser",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    },
    "AI Agent": {
      "main": [
        [
          {
            "node": "AI Agent1",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI Chat Model": {
      "ai_languageModel": [
        [
          {
            "node": "AI Agent",
            "type": "ai_languageModel",
            "index": 0
          },
          {
            "node": "AI Agent1",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "meta": null,
  "pinData": {},
  "versionId": "e00984a3-c69b-42b6-afb9-91b44c6a0e37",
  "triggerCount": 0,
  "tags": []
}
```
"""


PLANNER_PROMPT = r'''Given the user query as follows: 
{user_query}

Your task is to enrich the user's query by designing the n8n workflow in detail to achieve the user's goal.
You must design the n8n workflow in nature language instruction.
The instruction must include: The nodes and connections which include all the nodes and connections in the workflow
For the node instruction, it should have the node type, node title and the detail of node. Use the format "Create a [node type] with title [node title], it will be used to ....., [detail]"
For the connection instruction, it should show how the node is linked to other node. Use the fomat "Connect [Node A] to [Node B]"
Remark: Any trigger node must not in the middle of the workflow.

Your output must use the following format:
1. Task description (User's query)
2. The nodes
3. The connections'''


QUERY_PROMPT = r"""Here's the request:
```{query}```

You must think step by step and then generate the workflow json.
Your output must use the following format:
1. Task description (User's query)
2. The nodes
3. The connections
4. The workflow json
You must create a new json file for the n8n workflow at the end of the response.
In the workflow json, the type of the node must be one of the following:
```{node_types}```
Never use the node type that is not in the list.
And the version and parameters of the node must be align with the it's corresponding xxxx.node.ts file.
Make sure the connection is correctly set which the format is as the example.
"""

CREDENTIALS_PROMPT = r"""
Given the credentials list: {credentials}. Only create a new credentials if the credentials list do not contain the necessary credentials.
"""

DEBUG_PROMPT = r"""The workflow is as follows: 
```{workflow}``` 

Please modify the workflow according to the following feedback:
```{feedback}```

You must think step by step and then generate the workflow json.
You must create a new json file for the n8n workflow at the end of the response.
In the workflow json, the type of the node must be one of the following:
```{node_types}```
Never use the node type that is not in the list.
And the version and parameters of the node must be align with the it's corresponding xxxx.node.ts file.
Make sure the connection is correctly set which the format is as the example.
"""

# PLANNER_PROMPT = r"""Given the user query as follows: 
# ```{query}```

# Your task is to enrich the user's query by designing the n8n workflow in detail to achieve the user's goal. 
# You must design the n8n workflow in nature language instruction. 
# The instruction must include: The nodes and connections which include all the nodes and connections in the workflow 
# For the node instruction, it should have the node type, node title and the detail of node. 
# Use the format : 
# Create a *node type* with title *node title*, it will be used to ....., *detail*
# For the connection instruction, it should show how the node is linked to other node. Use the fomat Connect *Node A* to *Node B*

# Here is an exmaple for the output:
# **1. Task description**
# I would like to create a workflow to automate lead generation by identifying warm leads based on their hiring needs, personalizing outreach, and booking clients at scale. This workflow must include an Apify scraper to find companies actively hiring for specific roles on platforms like LinkedIn and a Large Language Model (LLM) like GPT-4o mini for enriching lead information and personalizing email content.

# **2. The nodes**
# Create a Schedule Trigger with title "Daily Lead Generation Trigger", it will be used to run the workflow automatically on a daily basis at 9 AM to search for new leads consistently.
# Create an HTTP Request with title "Apify LinkedIn Job Scraper", it will be used to call Apify API to scrape LinkedIn job postings for companies actively hiring in specific roles, filtering by keywords like "software engineer", "marketing manager", or target job titles.
# Create a Code with title "Process Scraped Job Data", it will be used to clean and structure the scraped job data, extract company information, job details, and hiring manager contact information from the raw Apify response.
# Create an If with title "Filter Valid Companies", it will be used to filter out companies that don't meet criteria such as company size, location, or industry, ensuring only qualified leads proceed through the workflow.
# Create an HTTP Request with title "Enrich Company Data", it will be used to call external APIs like Clearbit or Apollo to gather additional company information including revenue, employee count, recent news, and decision maker contacts.
# Create a LmChatOpenAi with title "Generate Lead Insights", it will be used to analyze the company data using GPT-4o mini to identify pain points, growth opportunities, and specific reasons why they might need your services based on their hiring patterns.
# Create a LmChatOpenAi with title "Personalize Email Content", it will be used to generate personalized outreach emails using GPT-4o mini, incorporating company-specific insights, hiring needs, and value propositions tailored to each prospect.
# Create a Gmail with title "Send Personalized Outreach Email", it will be used to send the personalized emails to decision makers at target companies, with proper tracking and follow-up sequences.
# Create a Google Sheets with title "Log Lead Activity", it will be used to record all lead interactions, email responses, and follow-up activities in a centralized spreadsheet for tracking and analytics.
# Create an If with title "Check Email Response", it will be used to monitor email responses and determine if prospects showed interest, requested a meeting, or need follow-up actions.
# Create an HTTP Request with title "Schedule Meeting via Calendly", it will be used to automatically send calendar booking links to interested prospects and handle meeting scheduling when they respond positively.
# Create a Wait with title "Follow-up Delay", it will be used to implement proper timing delays between follow-up emails, ensuring appropriate intervals and avoiding spam-like behavior.

# **3. The connections**
# Connect Daily Lead Generation Trigger to Apify LinkedIn Job Scraper
# Connect Apify LinkedIn Job Scraper to Process Scraped Job Data
# Connect Process Scraped Job Data to Filter Valid Companies
# Connect Filter Valid Companies to Enrich Company Data
# Connect Enrich Company Data to Generate Lead Insights
# Connect Generate Lead Insights to Personalize Email Content
# Connect Personalize Email Content to Send Personalized Outreach Email
# Connect Send Personalized Outreach Email to Log Lead Activity
# Connect Log Lead Activity to Check Email Response
# Connect Check Email Response to Schedule Meeting via Calendly
# Connect Check Email Response to Follow-up Delay
# Connect Follow-up Delay to Personalize Email Content

# Your output must use the following format: 
# 1. Task description (User's query) 
# 2. The nodes 
# 3. The connections Never include any other text in your output such as introduction, reference, Notes, etc.
# """

def get_planner_prompt(query):
    return PLANNER_PROMPT.format(user_query=query)

def get_create_prompt(query, credentials = None):
    node_types = get_node_types()

    if credentials:
        credentials_prompt = CREDENTIALS_PROMPT.format(credentials=credentials)

    else:
        credentials_prompt = ""
    return SYSTEM_PROMPT + credentials_prompt + QUERY_PROMPT.format(query=query, node_types=node_types)


def get_debug_prompt(workflow, feedback, credentials = None):
    node_types = get_node_types()

    if credentials:
        credentials_prompt = CREDENTIALS_PROMPT.format(credentials=credentials)

    else:
        credentials_prompt = ""

    return credentials_prompt + DEBUG_PROMPT.format(workflow=workflow, feedback=feedback, node_types=node_types)