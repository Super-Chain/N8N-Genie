# N8N-Genie
An AI-powered plugin for n8n that enhances workflow automation with intelligent code generation, repository analysis, and conversational assistance capabilities.

## Demo
https://github.com/user-attachments/assets/95540bb3-47f5-4ad5-b6ff-70a1f2de9a7d



## Features
### 1. AI-Powered Workflow Creation
- **Natural Language to n8n Workflow**: Transform user descriptions into complete n8n workflow JSON configurations
- **Intelligent Node Selection**: Automatically selects and configures appropriate n8n nodes based on workflow requirements
- **Smart Parameter Configuration**: AI determines optimal settings for each node in the workflow

### 2. Workflow Modification Assistant
- **Conversational Workflow Editing**: Modify existing workflows through natural language instructions
- **Intelligent Updates**: Add, remove, or modify nodes and connections based on user requests
- **Preserve Workflow Integrity**: Maintains existing workflow structure while applying requested changes

## Install 
**Step 1: Git Clone & Install Python Packages**
```
git clone https://github.com/Super-Chain/N8N-Genie.git
cd N8N-Genie
pip install -r requirements.txt
```

**Step 2: Set Up Environment Variables**

We are using [Open DeepWiki API](https://github.com/AsyncFuncAI/deepwiki-open/tree/main/api) `/api` folder

Create a .env file in the project root:
```
# Required API Keys
GOOGLE_API_KEY=your_google_api_key        # Required for Google Gemini models
OPENAI_API_KEY=your_openai_api_key        # Required for embeddings and OpenAI models

# Optional API Keys
OPENROUTER_API_KEY=your_openrouter_api_key  # Required only if using OpenRouter models

# OpenAI API Configuration
OPENAI_BASE_URL=https://custom-api-endpoint.com/v1  # Optional, for custom OpenAI API endpoints

```

**Step 3: Start the API Server** 

Using bash 

`uvicorn app:app --host 0.0.0.0 --port 1234`

Using Docker 
```
# Build the image (run this from the N8N-Genie directory)
docker build -t n8n-genie .

# Run the container (the .env file is now copied into the image)
docker run -d \
  --name n8n-genie-app \
  -p 1234:1234 \
  --env-file .env \
  n8n-genie
```

## N8N Installation

> ⚠️ **IMPORTANT WARNING**: Before proceeding with any installation method, **BACKUP YOUR EXISTING N8N DATA** to prevent any potential data loss during the plugin installation process. This includes workflows, credentials, and any custom configurations.

> 📋 **Docker Volume Reminder**: If you're using Docker for n8n, ensure you have proper volume mounts configured to persist your data. Example: `-v ~/.n8n:/home/node/.n8n` to maintain your workflows and settings across container restarts.

### Option 1: Fresh Installation (Local Host Fresh install)

Use this method if you're setting up n8n for the first time or want a clean installation with the N8N Genie plugin.

#### Build from n8n Repository

1. **Clone the official n8n repository**
   ```bash
   git clone https://github.com/n8n-io/n8n.git
   cd n8n
   ```

2. **Copy the N8N Genie plugin files**
   
   Copy the following files into the `docker/images/n8n` folder of the cloned n8n repo:
   - `plugin.js` - Main plugin frontend code
   - `apply_plugin.js` - Plugin injection script for the n8n interface
   
   ```bash
   cp ~/N8N-Genie/n8n-genie-js/plugin.js docker/images/n8n/
   cp ~/N8N-Genie/n8n-genie-js/apply_plugin.js docker/images/n8n/
   ```

3. **Modify the Dockerfile**
   
   Add the following lines to the `docker/images/n8n/Dockerfile` after the existing WORKDIR and COPY commands:

   Lookup the line `WORKDIR /home/node` and copy the following after this line
   
   ```dockerfile
    # Start with the official N8N image
    FROM docker.n8n.io/n8nio/n8n:latest
    
    # Switch to root to modify files
    USER root
    
    # Copy your custom files
    COPY docker/images/n8n/plugin.js /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/dist/assets/plugin.js
    COPY docker/images/n8n/apply_plugin.js /home/node/apply_plugin.js
    
    # Run your plugin script
    WORKDIR /home/node
    RUN node apply_plugin.js
    
    # Change port to 5678 (optional)
    ENV N8N_PORT=5679=8
    EXPOSE 5678
    
    # Switch back to node user
    USER node
    
    # Use the same entrypoint as the official image
    ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]
   ```
4. **Build Custom N8N image**
  ```bash
  docker build -t sc-n8n-custom .
  ```

5. **Run the enhanced n8n instance**
   ```bash
   docker volume create n8n_genie_data
   docker run -d --name sc-n8n -p 5678:5678 -v n8n_genie_data:/home/node/.n8n sc-n8n-custom

   ```

### Option 2: Existing N8N Instance Modification

Use this method if you already have a running n8n instance and want to add the N8N Genie plugin functionality.

> ⚠️ **CRITICAL**: This modification involves changes to your existing n8n installation. **BACKUP ALL YOUR DATA** before proceeding. Stop your current n8n instance and export all workflows as a precautionary measure.

#### For Docker-based Existing Installations

1. **Stop your current n8n container**
   ```bash
   docker stop your-n8n-container-name
   ```

2. **Backup your n8n data**
   ```bash
   # If using volume mounts
   cp -r ~/.n8n ~/.n8n-backup-$(date +%Y%m%d)
   
   # If using named volumes, backup with:
   docker run --rm -v your-n8n-volume:/source -v $(pwd):/backup alpine tar czf /backup/n8n-backup-$(date +%Y%m%d).tar.gz -C /source .
   ```

3. **Identify your current n8n container image and version**
   ```bash
   docker inspect your-n8n-container-name | grep Image
   ```

4. **Create a new Dockerfile for modification**
   ```dockerfile
   # Use your existing n8n image as base
   FROM n8nio/n8n:latest  # Replace with your current version
   
   USER root
   
   # Copy the N8N Genie plugin files
   COPY plugin.js /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/dist/assets/
   COPY apply_plugin.js /tmp/
   
   # Apply the plugin modifications
   RUN cd /tmp && node apply_plugin.js
   
   USER node
   ```

5. **Build the modified image**
   ```bash
   # Copy plugin files to current directory first
   cp ~/N8N-Genie/n8n-genie-js/plugin.js .
   cp ~/N8N-Genie/n8n-genie-js/apply_plugin.js .
   ```

6. **Run the modified n8n instance with data persistence**
   ```bash
   # Using volume mount (recommended)
   docker run -d --name sc-n8n \
     -p 5678:5678 \
     -v ~/.n8n:/home/node/.n8n \
     docker.n8n.io/n8nio/n8n
   ```
### Verification and Rollback

After installation, verify the plugin is working correctly:

1. **Access your n8n interface** at `http://localhost:5678`
2. **Look for the N8N Genie panel** in the sidebar
3. **Test basic functionality** by trying to create a simple workflow

**If something goes wrong:**
```bash
# For Docker installations
docker stop sc-n8n
docker run -d --name n8n-original -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n:latest
```

### Finish

The plugin will be available in your n8n interface with enhanced AI capabilities for workflow automation and code generation.

## Using the n8n N8N Genie

Once you have the N8N Genie plugin installed and running, you can leverage its powerful AI capabilities to enhance your n8n workflows. Here's how to get started:

### Accessing the N8N Genie

1. **Open your n8n interface** - Navigate to your n8n instance (typically at `http://localhost:5678`)
2. **Look for the N8N Genie panel** - The plugin will be available as a sidebar or overlay in your workflow editor
3. **Activate the Genie** - Click on the sidebar to open the assistant panel

### Basic Usage
You can use NotebookLM or other AI Chatbot to generate the prompt :
[Demo](https://www.linkedin.com/feed/update/urn:li:activity:7339230068948221952/)

#### 1. Workflow Generation
- **Click 'Create Workflow' button**: Redirect to the new page where you can start building your automation from scratch
- **Describe your automation**: Type a natural language description on the chat box of what you want to automate
- **Example**: 
```
**1. Task description**
I would like to create a workflow to automate lead generation by identifying warm leads based on their hiring needs, personalizing outreach, and booking clients at scale. This workflow must include an Apify scraper to find companies actively hiring for specific roles on platforms like LinkedIn and a Large Language Model (LLM) like GPT-4o mini for enriching lead information and personalizing email content.

**2. The nodes**
Create a Schedule Trigger with title "Daily Lead Generation Trigger", it will be used to run the workflow automatically on a daily basis at 9 AM to search for new leads consistently.
Create an HTTP Request with title "Apify LinkedIn Job Scraper", it will be used to call Apify API to scrape LinkedIn job postings for companies actively hiring in specific roles, filtering by keywords like "software engineer", "marketing manager", or target job titles.
Create a Code with title "Process Scraped Job Data", it will be used to clean and structure the scraped job data, extract company information, job details, and hiring manager contact information from the raw Apify response.
Create an If with title "Filter Valid Companies", it will be used to filter out companies that don't meet criteria such as company size, location, or industry, ensuring only qualified leads proceed through the workflow.
Create an HTTP Request with title "Enrich Company Data", it will be used to call external APIs like Clearbit or Apollo to gather additional company information including revenue, employee count, recent news, and decision maker contacts.
Create a LmChatOpenAi with title "Generate Lead Insights", it will be used to analyze the company data using GPT-4o mini to identify pain points, growth opportunities, and specific reasons why they might need your services based on their hiring patterns.
Create a LmChatOpenAi with title "Personalize Email Content", it will be used to generate personalized outreach emails using GPT-4o mini, incorporating company-specific insights, hiring needs, and value propositions tailored to each prospect.
Create a Gmail with title "Send Personalized Outreach Email", it will be used to send the personalized emails to decision makers at target companies, with proper tracking and follow-up sequences.
Create a Google Sheets with title "Log Lead Activity", it will be used to record all lead interactions, email responses, and follow-up activities in a centralized spreadsheet for tracking and analytics.
Create an If with title "Check Email Response", it will be used to monitor email responses and determine if prospects showed interest, requested a meeting, or need follow-up actions.
Create an HTTP Request with title "Schedule Meeting via Calendly", it will be used to automatically send calendar booking links to interested prospects and handle meeting scheduling when they respond positively.
Create a Wait with title "Follow-up Delay", it will be used to implement proper timing delays between follow-up emails, ensuring appropriate intervals and avoiding spam-like behavior.

**3. The connections**
Connect Daily Lead Generation Trigger to Apify LinkedIn Job Scraper
Connect Apify LinkedIn Job Scraper to Process Scraped Job Data
Connect Process Scraped Job Data to Filter Valid Companies
Connect Filter Valid Companies to Enrich Company Data
Connect Enrich Company Data to Generate Lead Insights
Connect Generate Lead Insights to Personalize Email Content
Connect Personalize Email Content to Send Personalized Outreach Email
Connect Send Personalized Outreach Email to Log Lead Activity
Connect Log Lead Activity to Check Email Response
Connect Check Email Response to Schedule Meeting via Calendly
Connect Check Email Response to Follow-up Delay
Connect Follow-up Delay to Personalize Email Content
```
- **Review**: The N8N Genie will generate a new workflow in JSON format, click the button "Copy Button" to copy the workflow JSON, then paste it on the n8n canvas to import and use the created workflow

#### 2. Workflow Modification
- **Navigate to existing workflow**: Go to the page of your existing workflow (the workflow must be saved) that you want to modify
- **Open the N8N Genie panel**: Click on the sidebar to activate the assistant
- **Describe your modifications**: Type instructions in the chatbox describing how you want to modify the current workflow
- **AI analysis**: The N8N Genie will read and analyze your existing workflow data automatically
- **Example**:
```
Modify the existing workflow by replaing the AI model from openAI to gemini
```
- **Review**: The N8N Genie will generate a separate workflow. Cick the button "Copy Button" to copy the workflow JSON, then paste it on the n8n canvas to import and use the created workflow

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Super-Chain/N8N-Genie&type=Date)](https://www.star-history.com/#Super-Chain/N8N-Genie&Date)
