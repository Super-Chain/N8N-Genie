import uvicorn
import json
from urllib.parse import unquote

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from adalflow.core.types import ModelType

import os
from dotenv import load_dotenv

load_dotenv()

from api.config import get_model_config, configs, OPENROUTER_API_KEY
from api.data_pipeline import count_tokens, get_file_content
from api.openrouter_client import OpenRouterClient
from api.rag import RAG

from prompt import get_create_prompt, get_debug_prompt, get_planner_prompt
from utils import clear_workflow

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FastAPI')

app = FastAPI(openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatCompletionRequest(BaseModel):
    query: str
    credentials: list
    workflow_data: str
    user: str

async def get_llm_response(prompt, provider, model_id):
    model = OpenRouterClient() 
    model_config = get_model_config(provider, model_id)["model_kwargs"]
    model_kwargs = {
        "model": model_id,
        "stream": False,  
        "temperature": model_config["temperature"],
        "top_p": model_config["top_p"]
    }
    api_kwargs = model.convert_inputs_to_api_kwargs(
        input=prompt,
        model_kwargs=model_kwargs,
        model_type=ModelType.LLM
    )
    response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)

    all_response = ""

    async for chunk in response:
        all_response += chunk

    logger.info(f"Planner response: {all_response}")

    return all_response

@app.post('/api/n8n/workflow')
async def chat_completions_stream(request: ChatCompletionRequest):
    """Stream a chat completion response directly using Google Generative AI"""
    logger.info(f"Received: {request.model_dump()}")
    credentials = request.credentials
    workflow_data = request.workflow_data
    filePath = None
    token = None
    type = "github"
    provider = "openrouter"
    model_id = "google/gemini-2.0-flash-001"
    language = "en"
    excluded_dirs = None
    excluded_files = None
    included_dirs = None
    included_files = None

    mode = 'create' if workflow_data == '' else 'debug'
    
    if mode == 'create':
        planner_prompt = get_planner_prompt(request.query)
        planner_response = await get_llm_response(planner_prompt, provider, model_id)
        formatted_prompt = get_create_prompt(planner_response, credentials)
    
    else:
        workflow = json.loads(workflow_data)
        workflow = clear_workflow(workflow) 
        formatted_prompt = get_debug_prompt(workflow, request.query, credentials)

    repo_url = "./databases/n8n-io_n8n.pkl" # "https://github.com/n8n-io/n8n/"

    messages = [
        ChatMessage(role="user", content=formatted_prompt)
    ]

    try:
        # Check if request contains very large input
        input_too_large = False
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if hasattr(last_message, 'content') and last_message.content:
                tokens = count_tokens(last_message.content, provider == "ollama")
                logger.info(f"Request size: {tokens} tokens")
                if tokens > 8000:
                    logger.warning(f"Request exceeds recommended token limit ({tokens} > 7500)")
                    input_too_large = True

        # Create a new RAG instance for this request
        try:
            request_rag = RAG(provider=provider, model=model_id)

            # Extract custom file filter parameters if provided
            excluded_dirs = None
            excluded_files = None
            included_dirs = None
            included_files = None

            if excluded_dirs:
                excluded_dirs = [unquote(dir_path) for dir_path in excluded_dirs.split('\n') if dir_path.strip()]
                logger.info(f"Using custom excluded directories: {excluded_dirs}")
            if excluded_files:
                excluded_files = [unquote(file_pattern) for file_pattern in excluded_files.split('\n') if file_pattern.strip()]
                logger.info(f"Using custom excluded files: {excluded_files}")
            if included_dirs:
                included_dirs = [unquote(dir_path) for dir_path in included_dirs.split('\n') if dir_path.strip()]
                logger.info(f"Using custom included directories: {included_dirs}")
            if included_files:
                included_files = [unquote(file_pattern) for file_pattern in included_files.split('\n') if file_pattern.strip()]
                logger.info(f"Using custom included files: {included_files}")

            request_rag.prepare_retriever(repo_url, type, token, excluded_dirs, excluded_files, included_dirs, included_files)
            logger.info(f"Retriever prepared for {repo_url}")
        except ValueError as e:
            if "No valid documents with embeddings found" in str(e):
                logger.error(f"No valid embeddings found: {str(e)}")
                raise HTTPException(status_code=500, detail="No valid document embeddings found. This may be due to embedding size inconsistencies or API errors during document processing. Please try again or check your repository content.")
            else:
                logger.error(f"ValueError preparing retriever: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error preparing retriever: {str(e)}")
        except Exception as e:
            logger.error(f"Error preparing retriever: {str(e)}")
            # Check for specific embedding-related errors
            if "All embeddings should be of the same size" in str(e):
                raise HTTPException(status_code=500, detail="Inconsistent embedding sizes detected. Some documents may have failed to embed properly. Please try again.")
            else:
                raise HTTPException(status_code=500, detail=f"Error preparing retriever: {str(e)}")

        # Validate request
        if not messages or len(messages) == 0:
            raise HTTPException(status_code=400, detail="No messages provided")

        last_message = messages[-1]
        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from the user")

        # Process previous messages to build conversation history
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                assistant_msg = messages[i + 1]

                if user_msg.role == "user" and assistant_msg.role == "assistant":
                    request_rag.memory.add_dialog_turn(
                        user_query=user_msg.content,
                        assistant_response=assistant_msg.content
                    )

        # Check if this is a Deep Research request
        is_deep_research = False
        research_iteration = 1

        # Process messages to detect Deep Research requests
        for msg in messages:
            if hasattr(msg, 'content') and msg.content and "[DEEP RESEARCH]" in msg.content:
                is_deep_research = True
                # Only remove the tag from the last message
                if msg == messages[-1]:
                    # Remove the Deep Research tag
                    msg.content = msg.content.replace("[DEEP RESEARCH]", "").strip()

        # Count research iterations if this is a Deep Research request
        if is_deep_research:
            research_iteration = sum(1 for msg in messages if msg.role == 'assistant') + 1
            logger.info(f"Deep Research request detected - iteration {research_iteration}")

            # Check if this is a continuation request
            if "continue" in last_message.content.lower() and "research" in last_message.content.lower():
                # Find the original topic from the first user message
                original_topic = None
                for msg in messages:
                    if msg.role == "user" and "continue" not in msg.content.lower():
                        original_topic = msg.content.replace("[DEEP RESEARCH]", "").strip()
                        logger.info(f"Found original research topic: {original_topic}")
                        break

                if original_topic:
                    # Replace the continuation message with the original topic
                    last_message.content = original_topic
                    logger.info(f"Using original topic for research: {original_topic}")

        # Get the query from the last message
        query = last_message.content

        # Only retrieve documents if input is not too large
        context_text = ""
        retrieved_documents = None

        if not input_too_large:
            try:
                # If filePath exists, modify the query for RAG to focus on the file
                rag_query = query
                if filePath:
                    # Use the file path to get relevant context about the file
                    rag_query = f"Contexts related to {filePath}"
                    logger.info(f"Modified RAG query to focus on file: {filePath}")

                # Try to perform RAG retrieval
                try:
                    # This will use the actual RAG implementation
                    retrieved_documents = request_rag(rag_query, language=language)

                    if retrieved_documents and retrieved_documents[0].documents:
                        # Format context for the prompt in a more structured way
                        documents = retrieved_documents[0].documents
                        logger.info(f"Retrieved {len(documents)} documents")

                        # Group documents by file path
                        docs_by_file = {}
                        for doc in documents:
                            file_path = doc.meta_data.get('file_path', 'unknown')
                            if file_path not in docs_by_file:
                                docs_by_file[file_path] = []
                            docs_by_file[file_path].append(doc)

                        # Format context text with file path grouping
                        context_parts = []
                        for file_path, docs in docs_by_file.items():
                            # Add file header with metadata
                            header = f"## File Path: {file_path}\n\n"
                            # Add document content
                            content = "\n\n".join([doc.text for doc in docs])

                            context_parts.append(f"{header}{content}")

                        # Join all parts with clear separation
                        context_text = "\n\n" + "-" * 10 + "\n\n".join(context_parts)
                    else:
                        logger.warning("No documents retrieved from RAG")
                except Exception as e:
                    logger.error(f"Error in RAG retrieval: {str(e)}")
                    # Continue without RAG if there's an error

            except Exception as e:
                logger.error(f"Error retrieving documents: {str(e)}")
                context_text = ""

        # Get repository information
        repo_url = repo_url
        repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url

        # Determine repository type
        repo_type = type

        # Get language information
        language_code = language or configs["lang_config"]["default"]
        supported_langs = configs["lang_config"]["supported_languages"]
        language_name = supported_langs.get(language_code, "English")

        # Create system prompt
        if is_deep_research:
            # Check if this is the first iteration
            is_first_iteration = research_iteration == 1

            # Check if this is the final iteration
            is_final_iteration = research_iteration >= 5

            if is_first_iteration:
                system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You are conducting a multi-turn Deep Research process to thoroughly investigate the specific topic in the user's query.
Your goal is to provide detailed, focused information EXCLUSIVELY about this topic.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- This is the first iteration of a multi-turn research process focused EXCLUSIVELY on the user's query
- Start your response with "## Research Plan"
- Outline your approach to investigating this specific topic
- If the topic is about a specific file or feature (like "Dockerfile"), focus ONLY on that file or feature
- Clearly state the specific topic you're researching to maintain focus throughout all iterations
- Identify the key aspects you'll need to research
- Provide initial findings based on the information available
- End with "## Next Steps" indicating what you'll investigate in the next iteration
- Do NOT provide a final conclusion yet - this is just the beginning of the research
- Do NOT include general repository information unless directly relevant to the query
- Focus EXCLUSIVELY on the specific topic being researched - do not drift to related topics
- Your research MUST directly address the original question
- NEVER respond with just "Continue the research" as an answer - always provide substantive research findings
- Remember that this topic will be maintained across all research iterations
</guidelines>

<style>
- Be concise but thorough
- Use markdown formatting to improve readability
- Cite specific files and code sections when relevant
</style>"""
            elif is_final_iteration:
                system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You are in the final iteration of a Deep Research process focused EXCLUSIVELY on the latest user query.
Your goal is to synthesize all previous findings and provide a comprehensive conclusion that directly addresses this specific topic and ONLY this topic.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- This is the final iteration of the research process
- CAREFULLY review the entire conversation history to understand all previous findings
- Synthesize ALL findings from previous iterations into a comprehensive conclusion
- Start with "## Final Conclusion"
- Your conclusion MUST directly address the original question
- Stay STRICTLY focused on the specific topic - do not drift to related topics
- Include specific code references and implementation details related to the topic
- Highlight the most important discoveries and insights about this specific functionality
- Provide a complete and definitive answer to the original question
- Do NOT include general repository information unless directly relevant to the query
- Focus exclusively on the specific topic being researched
- NEVER respond with "Continue the research" as an answer - always provide a complete conclusion
- If the topic is about a specific file or feature (like "Dockerfile"), focus ONLY on that file or feature
- Ensure your conclusion builds on and references key findings from previous iterations
</guidelines>

<style>
- Be concise but thorough
- Use markdown formatting to improve readability
- Cite specific files and code sections when relevant
- Structure your response with clear headings
- End with actionable insights or recommendations when appropriate
</style>"""
            else:
                system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You are currently in iteration {research_iteration} of a Deep Research process focused EXCLUSIVELY on the latest user query.
Your goal is to build upon previous research iterations and go deeper into this specific topic without deviating from it.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- CAREFULLY review the conversation history to understand what has been researched so far
- Your response MUST build on previous research iterations - do not repeat information already covered
- Identify gaps or areas that need further exploration related to this specific topic
- Focus on one specific aspect that needs deeper investigation in this iteration
- Start your response with "## Research Update {research_iteration}"
- Clearly explain what you're investigating in this iteration
- Provide new insights that weren't covered in previous iterations
- If this is iteration 3, prepare for a final conclusion in the next iteration
- Do NOT include general repository information unless directly relevant to the query
- Focus EXCLUSIVELY on the specific topic being researched - do not drift to related topics
- If the topic is about a specific file or feature (like "Dockerfile"), focus ONLY on that file or feature
- NEVER respond with just "Continue the research" as an answer - always provide substantive research findings
- Your research MUST directly address the original question
- Maintain continuity with previous research iterations - this is a continuous investigation
</guidelines>

<style>
- Be concise but thorough
- Focus on providing new information, not repeating what's already been covered
- Use markdown formatting to improve readability
- Cite specific files and code sections when relevant
</style>"""
        else:
            system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You provide direct, concise, and accurate information about code repositories.
You NEVER start responses with markdown headers or code fences.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- Answer the user's question directly without ANY preamble or filler phrases
- DO NOT include any rationale, explanation, or extra comments.
- DO NOT start with preambles like "Okay, here's a breakdown" or "Here's an explanation"
- DO NOT start with markdown headers like "## Analysis of..." or any file path references
- DO NOT start with ```markdown code fences
- DO NOT end your response with ``` closing fences
- DO NOT start by repeating or acknowledging the question
- JUST START with the direct answer to the question

<example_of_what_not_to_do>
```markdown
## Analysis of `adalflow/adalflow/datasets/gsm8k.py`

This file contains...
```
</example_of_what_not_to_do>

- Format your response with proper markdown including headings, lists, and code blocks WITHIN your answer
- For code analysis, organize your response with clear sections
- Think step by step and structure your answer logically
- Start with the most relevant information that directly addresses the user's query
- Be precise and technical when discussing code
- Your response language should be in the same language as the user's query
</guidelines>

<style>
- Use concise, direct language
- Prioritize accuracy over verbosity
- When showing code, include line numbers and file paths when relevant
- Use markdown formatting to improve readability
</style>"""

        # Fetch file content if provided
        file_content = ""
        if filePath:
            try:
                file_content = get_file_content(repo_url, filePath, type, token)
                logger.info(f"Successfully retrieved content for file: {filePath}")
            except Exception as e:
                logger.error(f"Error retrieving file content: {str(e)}")
                # Continue without file content if there's an error

        # Format conversation history
        conversation_history = ""
        for turn_id, turn in request_rag.memory().items():
            if not isinstance(turn_id, int) and hasattr(turn, 'user_query') and hasattr(turn, 'assistant_response'):
                conversation_history += f"<turn>\n<user>{turn.user_query.query_str}</user>\n<assistant>{turn.assistant_response.response_str}</assistant>\n</turn>\n"

        # Create the prompt with context
        prompt = f"/no_think {system_prompt}\n\n"

        if conversation_history:
            prompt += f"<conversation_history>\n{conversation_history}</conversation_history>\n\n"

        # Check if filePath is provided and fetch file content if it exists
        if file_content:
            # Add file content to the prompt after conversation history
            prompt += f"<currentFileContent path=\"{filePath}\">\n{file_content}\n</currentFileContent>\n\n"

        # Only include context if it's not empty
        CONTEXT_START = "<START_OF_CONTEXT>"
        CONTEXT_END = "<END_OF_CONTEXT>"
        if context_text.strip():
            prompt += f"{CONTEXT_START}\n{context_text}\n{CONTEXT_END}\n\n"
        else:
            # Add a note that we're skipping RAG due to size constraints or because it's the isolated API
            logger.info("No context available from RAG")
            prompt += "<note>Answering without retrieval augmentation.</note>\n\n"

        prompt += f"<query>\n{query}\n</query>\n\nAssistant: "

        model_config = get_model_config(provider, model_id)["model_kwargs"]

        if provider == "ollama":
            prompt += " /no_think"

            model = OllamaClient()
            model_kwargs = {
                "model": model_config["model"],
                "stream": True,
                "options": {
                    "temperature": model_config["temperature"],
                    "top_p": model_config["top_p"],
                    "num_ctx": model_config["num_ctx"]
                }
            }

            api_kwargs = model.convert_inputs_to_api_kwargs(
                input=prompt,
                model_kwargs=model_kwargs,
                model_type=ModelType.LLM
            )
        elif provider == "openrouter":
            logger.info(f"Using OpenRouter with model: {model_id}")

            # Check if OpenRouter API key is set
            if not OPENROUTER_API_KEY:
                logger.warning("OPENROUTER_API_KEY not configured, but continuing with request")
                # We'll let the OpenRouterClient handle this and return a friendly error message

            model = OpenRouterClient()
            model_kwargs = {
                "model": model_id,
                "stream": True,
                "temperature": model_config["temperature"],
                "top_p": model_config["top_p"]
            }

            api_kwargs = model.convert_inputs_to_api_kwargs(
                input=prompt,
                model_kwargs=model_kwargs,
                model_type=ModelType.LLM
            )
        elif provider == "openai":
            logger.info(f"Using Openai protocol with model: {model_id}")

            # Check if an API key is set for Openai
            if not OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not configured, but continuing with request")
                # We'll let the OpenAIClient handle this and return an error message

            # Initialize Openai client
            model = OpenAIClient()
            model_kwargs = {
                "model": model_id,
                "stream": True,
                "temperature": model_config["temperature"],
                "top_p": model_config["top_p"]
            }

            api_kwargs = model.convert_inputs_to_api_kwargs(
                input=prompt,
                model_kwargs=model_kwargs,
                model_type=ModelType.LLM
            )
        elif provider == "bedrock":
            logger.info(f"Using AWS Bedrock with model: {model_id}")

            # Check if AWS credentials are set
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                logger.warning("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not configured, but continuing with request")
                # We'll let the BedrockClient handle this and return an error message

            # Initialize Bedrock client
            model = BedrockClient()
            model_kwargs = {
                "model": model_id,
                "temperature": model_config["temperature"],
                "top_p": model_config["top_p"]
            }

            api_kwargs = model.convert_inputs_to_api_kwargs(
                input=prompt,
                model_kwargs=model_kwargs,
                model_type=ModelType.LLM
            )
        else:
            # Initialize Google Generative AI model
            model = genai.GenerativeModel(
                model_name=model_config["model"],
                generation_config={
                    "temperature": model_config["temperature"],
                    "top_p": model_config["top_p"],
                    "top_k": model_config["top_k"]
                }
            )

        # Create a streaming response
        async def response_stream():
            try:
                if provider == "ollama":
                    # Get the response and handle it properly using the previously created api_kwargs
                    response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                    # Handle streaming response from Ollama
                    async for chunk in response:
                        text = getattr(chunk, 'response', None) or getattr(chunk, 'text', None) or str(chunk)
                        if text and not text.startswith('model=') and not text.startswith('created_at='):
                            text = text.replace('<think>', '').replace('</think>', '')
                            yield text
                elif provider == "openrouter":
                    try:
                        # Get the response and handle it properly using the previously created api_kwargs
                        logger.info("Making OpenRouter API call")
                        response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                        # Handle streaming response from OpenRouter
                        async for chunk in response:
                            yield chunk
                    except Exception as e_openrouter:
                        logger.error(f"Error with OpenRouter API: {str(e_openrouter)}")
                        yield f"\nError with OpenRouter API: {str(e_openrouter)}\n\nPlease check that you have set the OPENROUTER_API_KEY environment variable with a valid API key."
                elif provider == "openai":
                    try:
                        # Get the response and handle it properly using the previously created api_kwargs
                        logger.info("Making Openai API call")
                        response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                        # Handle streaming response from Openai
                        async for chunk in response:
                           choices = getattr(chunk, "choices", [])
                           if len(choices) > 0:
                               delta = getattr(choices[0], "delta", None)
                               if delta is not None:
                                    text = getattr(delta, "content", None)
                                    if text is not None:
                                        yield text
                    except Exception as e_openai:
                        logger.error(f"Error with Openai API: {str(e_openai)}")
                        yield f"\nError with Openai API: {str(e_openai)}\n\nPlease check that you have set the OPENAI_API_KEY environment variable with a valid API key."
                elif provider == "bedrock":
                    try:
                        # Get the response and handle it properly using the previously created api_kwargs
                        logger.info("Making AWS Bedrock API call")
                        response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                        # Handle response from Bedrock (not streaming yet)
                        if isinstance(response, str):
                            yield response
                        else:
                            # Try to extract text from the response
                            yield str(response)
                    except Exception as e_bedrock:
                        logger.error(f"Error with AWS Bedrock API: {str(e_bedrock)}")
                        yield f"\nError with AWS Bedrock API: {str(e_bedrock)}\n\nPlease check that you have set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables with valid credentials."
                else:
                    # Generate streaming response
                    response = model.generate_content(prompt, stream=True)
                    # Stream the response
                    for chunk in response:
                        if hasattr(chunk, 'text'):
                            yield chunk.text

            except Exception as e_outer:
                logger.error(f"Error in streaming response: {str(e_outer)}")
                error_message = str(e_outer)

                # Check for token limit errors
                if "maximum context length" in error_message or "token limit" in error_message or "too many tokens" in error_message:
                    # If we hit a token limit error, try again without context
                    logger.warning("Token limit exceeded, retrying without context")
                    try:
                        # Create a simplified prompt without context
                        simplified_prompt = f"/no_think {system_prompt}\n\n"
                        if conversation_history:
                            simplified_prompt += f"<conversation_history>\n{conversation_history}</conversation_history>\n\n"

                        # Include file content in the fallback prompt if it was retrieved
                        if filePath and file_content:
                            simplified_prompt += f"<currentFileContent path=\"{filePath}\">\n{file_content}\n</currentFileContent>\n\n"

                        simplified_prompt += "<note>Answering without retrieval augmentation due to input size constraints.</note>\n\n"
                        simplified_prompt += f"<query>\n{query}\n</query>\n\nAssistant: "

                        if provider == "ollama":
                            simplified_prompt += " /no_think"

                            # Create new api_kwargs with the simplified prompt
                            fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                                input=simplified_prompt,
                                model_kwargs=model_kwargs,
                                model_type=ModelType.LLM
                            )

                            # Get the response using the simplified prompt
                            fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                            # Handle streaming fallback_response from Ollama
                            async for chunk in fallback_response:
                                text = getattr(chunk, 'response', None) or getattr(chunk, 'text', None) or str(chunk)
                                if text and not text.startswith('model=') and not text.startswith('created_at='):
                                    text = text.replace('<think>', '').replace('</think>', '')
                                    yield text
                        elif provider == "openrouter":
                            try:
                                # Create new api_kwargs with the simplified prompt
                                fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                                    input=simplified_prompt,
                                    model_kwargs=model_kwargs,
                                    model_type=ModelType.LLM
                                )

                                # Get the response using the simplified prompt
                                logger.info("Making fallback OpenRouter API call")
                                fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                                # Handle streaming fallback_response from OpenRouter
                                async for chunk in fallback_response:
                                    yield chunk
                            except Exception as e_fallback:
                                logger.error(f"Error with OpenRouter API fallback: {str(e_fallback)}")
                                yield f"\nError with OpenRouter API fallback: {str(e_fallback)}\n\nPlease check that you have set the OPENROUTER_API_KEY environment variable with a valid API key."
                        elif provider == "openai":
                            try:
                                # Create new api_kwargs with the simplified prompt
                                fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                                    input=simplified_prompt,
                                    model_kwargs=model_kwargs,
                                    model_type=ModelType.LLM
                                )

                                # Get the response using the simplified prompt
                                logger.info("Making fallback Openai API call")
                                fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                                # Handle streaming fallback_response from Openai
                                async for chunk in fallback_response:
                                    text = chunk if isinstance(chunk, str) else getattr(chunk, 'text', str(chunk))
                                    yield text
                            except Exception as e_fallback:
                                logger.error(f"Error with Openai API fallback: {str(e_fallback)}")
                                yield f"\nError with Openai API fallback: {str(e_fallback)}\n\nPlease check that you have set the OPENAI_API_KEY environment variable with a valid API key."
                        elif provider == "bedrock":
                            try:
                                # Create new api_kwargs with the simplified prompt
                                fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                                    input=simplified_prompt,
                                    model_kwargs=model_kwargs,
                                    model_type=ModelType.LLM
                                )

                                # Get the response using the simplified prompt
                                logger.info("Making fallback AWS Bedrock API call")
                                fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                                # Handle response from Bedrock
                                if isinstance(fallback_response, str):
                                    yield fallback_response
                                else:
                                    # Try to extract text from the response
                                    yield str(fallback_response)
                            except Exception as e_fallback:
                                logger.error(f"Error with AWS Bedrock API fallback: {str(e_fallback)}")
                                yield f"\nError with AWS Bedrock API fallback: {str(e_fallback)}\n\nPlease check that you have set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables with valid credentials."
                        else:
                            # Initialize Google Generative AI model
                            model_config = get_model_config(provider, model_id)
                            fallback_model = genai.GenerativeModel(
                                model_name=model_config["model"],
                                generation_config={
                                    "temperature": model_config["model_kwargs"].get("temperature", 0.7),
                                    "top_p": model_config["model_kwargs"].get("top_p", 0.8),
                                    "top_k": model_config["model_kwargs"].get("top_k", 40)
                                }
                            )

                            # Get streaming response using simplified prompt
                            fallback_response = fallback_model.generate_content(simplified_prompt, stream=True)
                            # Stream the fallback response
                            for chunk in fallback_response:
                                if hasattr(chunk, 'text'):
                                    yield chunk.text
                    except Exception as e2:
                        logger.error(f"Error in fallback streaming response: {str(e2)}")
                        yield f"\nI apologize, but your request is too large for me to process. Please try a shorter query or break it into smaller parts."
                else:
                    # For other errors, return the error message
                    yield f"\nError: {error_message}"

        # Return streaming response
        return StreamingResponse(response_stream())

    except HTTPException:
        raise
    except Exception as e_handler:
        error_msg = f"Error in streaming chat completion: {str(e_handler)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234)
