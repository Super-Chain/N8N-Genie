class RefImpl {
  constructor(initialValue) {
    this.value = initialValue;
  }
}

const isSending = new RefImpl(false);
const chatMessage = new RefImpl('');
const chatHistory2 = new RefImpl([]);
const codeResponse = new RefImpl([]);
const streamResponse = new RefImpl('');
const isChatOpen = new RefImpl(false);

function parseWorkflowId(path) {
    const pattern = /workflow\/(.*)/;
    const match = path.match(pattern);

    if (match) {
        const workflowId = match[1].split('/')[0];

        if (workflowId.includes('new')) {
            return null;
        }

        return workflowId;
    } else {
        return null;
    }
}

function parseExecutionId(path) {
    const pattern = /executions\/(.*)/;
    const match = path.match(pattern);

    if (match) {
        return match[1];
    } else {
        return null;
    }
}

async function getUser() {
  const origin = window.location.origin;
  const browserId = localStorage.getItem('n8n-browserId');
  const url = `${origin}/rest/login`;

  const headers = {
    'browser-id': browserId,
  };

  const response = await fetch(url, { headers, credentials: 'include' });

  if (response.status !== 200) {
    return '';
  }

  const data = await response.json();
  let user = data.data;

  return JSON.stringify(user);
} 
    
async function getCredentials() {
  const origin = window.location.origin;
  const browserId = localStorage.getItem('n8n-browserId');
  const url = `${origin}/rest/credentials?includeScopes=true&includeData=true`;

  const headers = {
      'browser-id': browserId,
  };

  const response = await fetch(url, { headers, credentials: 'include' });

  if (response.status !== 200) {
      const responseText = await response.text();
      return { error: 'Failed to get credentials', response: responseText };
  }

  const data = await response.json();
  let credentials = data.data;

  if (Array.isArray(credentials)) {
      credentials = credentials.map(credential => ({
          id: credential.id,
          name: credential.name,
          type: credential.type
      }));
  }
  
  return credentials;
}

// async function getExecutionData() {
//   const executionId = parseExecutionId(window.location.pathname);

//   if (!executionId) {
//     return '';
//   }

//   const origin = window.location.origin;
//   const browserId = localStorage.getItem('n8n-browserId');
//   const url = `${origin}/rest/executions/${executionId}`;

//   const headers = {
//       'browser-id': browserId,
//   };

//   const response = await fetch(url, { headers, credentials: 'include' });

//   if (response.status !== 200) {
//       const responseText = await response.text();
//       return { error: 'Failed to get execution data', response: responseText };
//   }

//   const data = await response.json();
//   let executionData = data.data;
//   executionData.data = JSON.parse(executionData.data);

//   return executionData;
// }

async function getWorkflowData() {
  const workflowId = parseWorkflowId(window.location.pathname);

  if (!workflowId) {
    return '';
  }

  const origin = window.location.origin;
  const browserId = localStorage.getItem('n8n-browserId');
  const url = `${origin}/rest/workflows/${workflowId}`;

  const headers = {
      'browser-id': browserId,
  };

  const response = await fetch(url, { headers, credentials: 'include' });

  if (response.status !== 200) {
      const responseText = await response.text();
      return { error: 'Failed to get workflow data', response: responseText };
  }

  const data = await response.json();
  const workflowData = data.data;

  return JSON.stringify(workflowData);
}

    
const sendChatMessage = async () => {
  if (!chatMessage.value.trim() || isSending.value) return;
  const button = document.getElementById('send-button');

  const textarea = document.getElementById('request-input');
  textarea.value = '';
  textarea.rows = 3;

  try {
    button.innerHTML = `
    <span class="_icon_g7qox_727"><span class="n8n-spinner"><span class="n8n-text _compact_ihh15_156 _size-medium_ihh15_141 _regular_ihh15_127 n8n-icon n8n-icon"><svg class="svg-inline--fa fa-spinner fa-w-16 fa-spin _medium_1cwxf_131" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="spinner" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path class="" fill="currentColor" d="M304 48c0 26.51-21.49 48-48 48s-48-21.49-48-48 21.49-48 48-48 48 21.49 48 48zm-48 368c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zm208-208c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zM96 256c0-26.51-21.49-48-48-48S0 229.49 0 256s21.49 48 48 48 48-21.49 48-48zm12.922 99.078c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.491-48-48-48zm294.156 0c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.49-48-48-48zM108.922 60.922c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.491-48-48-48z"></path></svg></span></span></span>
     Send
     `;
    isSending.value = true;
    streamResponse.value = "";

    const currentMessage = chatMessage.value;
    chatMessage.value = "";
    chatHistory2.value.push({
      message: currentMessage,
      response: ""
    });
    codeResponse.value.push('');
    updateChatDisplay();

    const credentials = await getCredentials();
    const workflowData = await getWorkflowData();
    const user = await getUser();
    // const executionData = await getExecutionData();

    let body = {
      query: currentMessage,
      credentials: credentials,
      workflow_data: workflowData,
      user: user,
      // execution_log: JSON.stringify(executionData),
    };

    console.log('body', body);
    
    const apiBaseUrl = `https://fdts4d5w3m.us-east-1.awsapprunner.com`;
    const response = await fetch(`${apiBaseUrl}/api/n8n/workflow`, { 
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
      mode: "cors",
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error("Failed to send message");
    }
    const reader = response.body?.getReader();
    if (!reader) return;
    
    var stream = "";
    var code_response = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = new TextDecoder().decode(value);

      if (stream === '') {
        stream = text.trim();
      } else {
        stream += text;
      }

      stream += '[NEW_LINE]';
      
      stream.split(/(```json[\s\S]*?```)/).map((part, i) => {
        if (part.includes('```json')) {
          code_response = part;
          codeResponse.value[codeResponse.value.length - 1] = code_response.replace('```json', '').replace('```', '').replaceAll('[NEW_LINE]', '');
        }
      });

      if (code_response.trim() != "") {
        chatHistory2.value[chatHistory2.value.length - 1].response = stream.replace(code_response, "").replaceAll('[NEW_LINE]', '\n');
        
      } else {
        chatHistory2.value[chatHistory2.value.length - 1].response = stream.replaceAll('[NEW_LINE]', '\n');
      };
      
      // Update the UI to show streaming response
      updateChatDisplay();
    }
  } catch (error) {
    console.error("Error sending message:", error);
  } finally {
    button.innerHTML = `Send`;
    isSending.value = false;
  }
};

const handleKeyPress = (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
    
  }
};

const updateSendButtonState = (textarea, sendButton) => {
  if (textarea.value.trim() !== '') {
    sendButton.disabled = false;
    sendButton.classList.remove('_disabled_g7qox_402');
    sendButton.setAttribute('aria-disabled', 'false');
  } else {
    sendButton.disabled = true;
    sendButton.classList.add('_disabled_g7qox_402');
    sendButton.setAttribute('aria-disabled', 'true');
  }
};

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value;
  if (isChatOpen.value) {
    document.querySelector('._chatSidebar_ihiut_213').className = '_chatSidebar_ihiut_213 _open_ihiut_225';
    document.querySelector('._chatToggle_ihiut_229').innerHTML = `
    <svg viewBox="0 0 24 24" width="16px" height="16px" class="n8n-icon ml-5xs" aria-hidden="true" focusable="false" role="img" data-icon="chevron-right">
        <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 18l6-6l-6-6"></path>
    </svg>
    `;
  } else {
    document.querySelector('._chatSidebar_ihiut_213').className = '_chatSidebar_ihiut_213';
    document.querySelector('._chatToggle_ihiut_229').innerHTML = `
    <svg viewBox="0 0 24 24" width="16px" height="16px" class="n8n-icon ml-5xs" aria-hidden="true" focusable="false" role="img" data-icon="chevron-left">
        <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 18l-6-6l6-6"></path>
    </svg>`;
  }


  
};

const updateChatDisplay = () => {
  const messagesContainer = document.querySelector('._messages_ihiut_275');
  if (!messagesContainer) return;
  
  // Clear existing messages
  messagesContainer.innerHTML = '';
  
  // Render chat history
  chatHistory2.value.forEach((chat, index) => {
    const chatItem = document.createElement('div');
    chatItem.className = '_chatItem_ihiut_281';
    
    // User message
    const userMessage = document.createElement('div');
    userMessage.className = '_userMessage_ihiut_287';
    userMessage.innerHTML = `<strong>You:</strong> ${chat.message}`;
    
    // AI response
    const aiResponse = document.createElement('div');
    aiResponse.className = '_aiResponse_ihiut_288';
    aiResponse.innerHTML = `<strong>Assistant:</strong> ${chat.response}`;
    
    // Code response if available
    if (codeResponse.value[index] && codeResponse.value[index] != '') {
      const codeBlock = document.createElement('code');
      codeBlock.style.display = 'block';
      codeBlock.style.whiteSpace = 'pre-wrap';
      codeBlock.style.color = '#d63384';
      codeBlock.style.backgroundColor = '#f0f0f0';
      codeBlock.textContent = codeResponse.value[index];
      aiResponse.appendChild(codeBlock);

      const copyButton = document.createElement('button');
      copyButton.className = 'button _button_g7qox_351 _primary_g7qox_611 _medium_g7qox_579';
      copyButton.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: white;
            padding: 8px 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 80px;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
        `;

      copyButton.ariaLabel = codeResponse.value[index];
      copyButton.innerHTML = `<div style="display: flex; align-items: center;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15V5a2 2 0 0 1 2-2h8"></path></svg><span style="margin-left:4px;">Copy Workflow</span></div>`;
      copyButton.onclick = () => {
        navigator.clipboard.writeText(copyButton.ariaLabel);

        copyButton.className = 'button _button_g7qox_351 _primary_g7qox_611 _medium_g7qox_579 _disabled_g7qox_402';
        copyButton.style.cssText = `
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            border-radius: 8px;
            color: white;
            padding: 8px 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 80px;
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
        `;
        copyButton.innerHTML = `<div style="display: flex; align-items: center;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3"><polyline points="20,6 9,17 4,12"></polyline></svg><span style="margin-left:4px;">Copied!</span></div>`;
        
        setTimeout(() => {
          copyButton.className = 'button _button_g7qox_351 _primary_g7qox_611 _medium_g7qox_579';
          copyButton.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: white;
            padding: 8px 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 80px;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
          `;
          copyButton.innerHTML = `<div style="display: flex; align-items: center;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15V5a2 2 0 0 1 2-2h8"></path></svg><span style="margin-left:4px;">Copy Workflow</span></div>`;
        }, 3000);
      };
      aiResponse.appendChild(copyButton);
    }
    
    chatItem.appendChild(userMessage);
    chatItem.appendChild(aiResponse);
    messagesContainer.appendChild(chatItem);
  });
  
  // Show streaming response if available
  if (streamResponse.value) {
    const streamItem = document.createElement('div');
    streamItem.className = '_chatItem_ihiut_281';
    
    const streamingResponse = document.createElement('div');
    streamingResponse.className = '_aiResponse_ihiut_288';
    streamingResponse.innerHTML = `<strong>Assistant:</strong> ${streamResponse.value}`;
    
    streamItem.appendChild(streamingResponse);
    messagesContainer.appendChild(streamItem);
  }
};

// CSS styles wrapped in a style tag
const styles = `
<style>
._chatSidebar_ihiut_213 {
  position: fixed;
  top: 0;
  right: -700px;
  width: 700px;
  height: 100vh;
  background: var(--color-background-xlight);
  border-left: 1px solid var(--color-foreground-base);
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
}
._chatSidebar_ihiut_213._open_ihiut_225 {
  right: 0;
}
._chatToggle_ihiut_229 {
  position: absolute;
  left: -32px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 48px;
  background: var(--color-background-xlight);
  border: 1px solid var(--color-foreground-base);
  border-right: none;
  border-radius: 4px 0 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
._chatToggle_ihiut_229:hover {
  background: var(--color-background-light);
}
._chatToggle_ihiut_229 svg {
  width: 16px;
  height: 16px;
  color: var(--color-text-dark);
}
._chatContent_ihiut_249 {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}
._chatHeader_ihiut_256 {
  padding: var(--spacing-s);
  border-bottom: 1px solid var(--color-foreground-base);
}
._chatHeader_ihiut_256 h2 {
  margin: 0;
  font-size: var(--font-size-m);
}
._chatHistory_ihiut_265 {
  flex: 1;
  padding: var(--spacing-s);
  overflow-y: auto;
}
._chatHistory_ihiut_265 h3 {
  margin: 0 0 var(--spacing-s);
  font-size: var(--font-size-s);
}
._messages_ihiut_275 {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-s);
}
._chatItem_ihiut_281 {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xs);
}
._userMessage_ihiut_287,
._aiResponse_ihiut_288 {
  padding: var(--spacing-2xs) var(--spacing-xs);
  border-radius: var(--border-radius-base);
  white-space: pre-line;
}
._userMessage_ihiut_287 strong,
._aiResponse_ihiut_288 strong {
  display: block;
  margin-bottom: var(--spacing-4xs);
}
._userMessage_ihiut_287 {
  background: var(--color-background-light);
  align-self: flex-end;
  max-width: 80%;
}
._aiResponse_ihiut_288 {
  background: var(--color-background-base);
  align-self: flex-start;
  max-width: 80%;
}
._chatControls_ihiut_311 {
  padding: var(--spacing-s);
  border-top: 1px solid var(--color-foreground-base);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-s);
}
._inputContainer_ihiut_330 {
  display: flex;
  gap: var(--spacing-2xs);
}
._inputContainer_ihiut_330 .n8n-input {
  flex: 1;
}
._inputContainer_ihiut_330 .n8n-button {
  align-self: flex-end;
}

/* Loading spinner styles */
.n8n-spinner {
  display: inline-block;
  animation: n8n-spin 1s linear infinite;
}

@keyframes n8n-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.n8n-spinner svg {
  animation: fa-spin 2s linear infinite;
}

@keyframes fa-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.fa-spin {
  animation: fa-spin 2s linear infinite;
}

/* Icon styles for spinner */
.n8n-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

._icon_g7qox_727 {
  display: inline-flex;
  align-items: center;
  margin-right: 4px;
}

/* Medium size icon */
._medium_1cwxf_131 {
  width: 16px;
  height: 16px;
}

/* Text styles */
._compact_ihh15_156 {
  line-height: 1.2;
}

._size-medium_ihh15_141 {
  font-size: 14px;
}

._regular_ihh15_127 {
  font-weight: 400;
}
</style>
`;

function initializeChat() {
    // Inject CSS styles
    document.head.insertAdjacentHTML('beforeend', styles);

    // Find the div with id="sidebar"
    const sidebar = document.getElementById('sidebar');

    if (sidebar) {
        // Create a new element (e.g., a div)
        const newElement = document.createElement('div');
        newElement.className = '_chatSidebar_ihiut_213';

        // Create chat toggle element
        const chatToggle = document.createElement('div');
        chatToggle.className = '_chatToggle_ihiut_229';
        chatToggle.onclick = toggleChat;
        chatToggle.innerHTML = `
            <svg viewBox="0 0 24 24" width="10px" height="10px" class="n8n-icon ml-5xs" aria-hidden="true" focusable="false" role="img" data-icon="chevron-left">
                <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 18l-6-6l6-6"></path>
            </svg>
        `;

        // Create chat content element
        const chatContent = document.createElement('div');
        chatContent.className = '_chatContent_ihiut_249';
        
        // Create chat header
        const chatHeader = document.createElement('div');
        chatHeader.className = '_chatHeader_ihiut_256';
        chatHeader.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h2 style="margin: 0; color: white; font-size: 18px; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 8px;">
                        N8N Genie
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" style="width: 28px; height: 28px;"><path fill="#88C9F9" d="M32 36v-2c0-3.313-2.687-6-6-6H10c-3.313 0-6 2.687-6 6v2h28z"/><path fill="#88C9F9" d="M13.64 28.101c1.744 1.267 2.849 3.728 4.36 3.728 1.511 0 2.616-2.462 4.36-3.728V24.29h-8.72v3.811zm-2.196-12.166c0 1.448-.734 2.622-1.639 2.622C8.9 18.558 8 17.448 8 16c0-1.935.501-2.687 1.806-2.687.905 0 1.638 1.174 1.638 2.622zM28 16c0 1.448-.9 2.558-1.806 2.558-.905 0-1.639-1.174-1.639-2.622s.734-2.623 1.639-2.623c1.352 0 1.806.752 1.806 2.687z"/><path fill="#88C9F9" d="M9.478 16.96C9.478 11.371 11 5 18 5s8.522 6.371 8.522 11.96C26.522 22 24 27.08 18 27.08S9.478 22 9.478 16.96z"/><path fill="#662113" d="M21.703 16.908h-.145c-.459 0-.835-.376-.835-.835V15.02c0-.459.376-.835.835-.835h.145c.459 0 .835.376.835.835v1.053c0 .459-.375.835-.835.835zm-7.406 0h.145c.459 0 .835-.376.835-.835V15.02c0-.459-.376-.835-.835-.835h-.145c-.459 0-.835.376-.835.835v1.053c0 .459.375.835.835.835z"/><path fill="#269" d="M18.007 23.802c2.754 0 3.6-.706 3.741-.848.256-.256.256-.671 0-.927-.248-.248-.645-.255-.902-.024-.052.038-.721.487-2.839.487-2.2 0-2.836-.485-2.842-.49-.255-.255-.656-.243-.913.013-.256.256-.242.684.014.94.141.143.987.849 3.741.849z"/><path fill="#55ACEE" d="M18.75 19.75h-1.5c-.413 0-.75-.337-.75-.75s.337-.75.75-.75h1.5c.413 0 .75.337.75.75s-.337.75-.75.75z"/><path fill="#744EAA" d="M12.016 27.95s-.157 6.817 3.987 6.817V36H8.984S8.77 30.076 10 28l2.016-.05zm11.955 0s.157 6.817-3.987 6.817V36h7.019s.214-5.924-1.016-8l-2.016-.05zM18 8.934s7.149 1.858 8.245 5.204c.478-1.021.755-3.257.755-4.518C27 5.781 24 3 19.125 3h-2.25C12.75 3 9 5.781 9 9.62c0 1.262.277 3.664.754 4.684C10.851 10.957 18 8.934 18 8.934z"/><g fill="#CBB7EA"><path d="M26.985 10.177c-1.396-1.115-3.044-2.037-4.612-2.559-.365-.122-.755.076-.876.437-.121.363.075.755.438.876 1.666.555 3.495 1.666 4.882 2.935.09-.623.151-1.328.168-1.689zM9.117 11.311c2.007-1.436 8.723-5.759 16.398-5.819-.473-.545-.984-.937-1.579-1.308-6.706.498-12.428 3.839-14.931 5.522.01.455.046 1.013.112 1.605z"/><path d="M26.421 6.89c-.028-.004-.084 0-.113 0-2.835 0-5.703.71-8.528 2.108.139-.042.22-.064.22-.064s.815.212 1.937.621c2.126-.845 4.263-1.28 6.371-1.28.203 0 .404.014.573.052-.075-.419-.248-1.011-.46-1.437zM9.188 8.036c2.477-1.586 7.101-3.872 12.342-4.784C20.734 3.016 19.983 3 19.125 3H17.36c-2.725 1.059-5.152 1.857-7.022 2.887-.536.678-.934 1.314-1.15 2.149z"/></g><path fill="#FFD983" d="M18.112 5.887c.887 0 1.612.726 1.612 1.612V9.15c0 .887-.726 1.612-1.612 1.612-.887 0-1.612-.726-1.612-1.612V7.499c0-.887.726-1.612 1.612-1.612z"/><path fill="#FFAC33" d="M18.112 6.89c.484 0 .881.396.881.881v1.108c0 .484-.396.881-.881.881-.484 0-.881-.396-.881-.881V7.771c.001-.485.397-.881.881-.881z"/><path d="M26.546 20.159c.032-.204-.107-.396-.312-.428-.209-.039-.396.108-.428.312-.01.064-1.072 6.251-7.231 6.625.111-.968-.078-1.805-.088-1.846-.063-.27-.334-.44-.602-.372-.269.063-.435.332-.372.601.002.009.178.784.052 1.627-6.269-.28-7.328-6.37-7.37-6.636-.033-.204-.224-.344-.429-.312-.204.032-.344.224-.312.428.008.049.567 3.305 3.133 5.45.007.017.026.04.07.078.749.646 3.923 3.988 5.34 4.061v.001l.004-.001.004.001v-.001c1.416-.073 4.591-3.415 5.34-4.061.043-.037.062-.06.07-.077 2.564-2.144 3.124-5.401 3.131-5.45z"/></svg>
                    </h2>
                    <div style="width: 1px; height: 20px; background: rgba(255,255,255,0.3);"></div>
                    <span style="color: rgba(255,255,255,0.9); font-size: 12px; font-weight: 400;">Your AI-powered n8n workflow assistant</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 8px rgba(74, 222, 128, 0.5);"></div>
                    <span style="color: rgba(255,255,255,0.8); font-size: 11px;">Online</span>
                </div>
            </div>
        `;

        
        // Create chat history
        const chatHistory = document.createElement('div');
        chatHistory.className = '_chatHistory_ihiut_265';
        
        const messages = document.createElement('div');
        messages.className = '_messages_ihiut_275';
        chatHistory.appendChild(messages);
        
        // Create chat controls
        const chatControls = document.createElement('div');
        chatControls.className = '_chatControls_ihiut_311';
        chatControls.style.cssText = `
            padding: 16px;
            border-top: 1px solid #e5e7eb;
            background: #fafafa;
        `;
        
        const inputContainer = document.createElement('div');
        inputContainer.className = '_inputContainer_ihiut_330';
        inputContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: border-color 0.2s ease;
        `;
        
        // Create textarea container
        const textareaContainer = document.createElement('div');
        textareaContainer.className = 'el-textarea el-input--large n8n-input';
        textareaContainer.style.cssText = `
            width: 100%;
            margin: 0;
        `;
        
        const textarea = document.createElement('textarea');
        textarea.className = 'el-textarea__inner';
        textarea.name = 'input-ssh6zmkvr';
        textarea.rows = 3;
        textarea.addEventListener('input', function() {
            // Reset to single row to get accurate scrollHeight
            this.rows = 3;
            
            // Calculate required rows based on content
            const lineHeight = parseInt(window.getComputedStyle(this).lineHeight) || 20;
            const padding = 32; // top + bottom padding
            const minHeight = 60;
            const maxRows = 12;
            
            const scrollHeight = this.scrollHeight;
            const requiredHeight = Math.max(minHeight, scrollHeight);
            const calculatedRows = Math.min(maxRows, Math.max(1, Math.ceil((requiredHeight - padding) / lineHeight)));
            
            this.rows = calculatedRows;
        });
        textarea.title = '';
        textarea.tabIndex = 0;
        textarea.autocomplete = 'off';
        textarea.placeholder = 'Describe your workflow or ask for help...';
        textarea.id = 'request-input';
        textarea.style.cssText = `
            border: none;
            outline: none;
            resize: none;
            font-size: 14px;
            line-height: 1.5;
            color: #374151;
            background: transparent;
            width: 100%;
            min-height: 60px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        textarea.onkeydown = handleKeyPress;
        
        // Add focus/blur handlers for container border
        textarea.addEventListener('focus', () => {
            inputContainer.style.borderColor = '#667eea';
            inputContainer.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
        });
        
        textarea.addEventListener('blur', () => {
            inputContainer.style.borderColor = '#d1d5db';
            inputContainer.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
        });
        
        textareaContainer.appendChild(textarea);
        
        // Create send button container
        const sendButtonContainer = document.createElement('div');
        sendButtonContainer.style.cssText = `
            display: flex;
            justify-content: flex-end;
            align-items: center;
        `;
        
        // Create send button
        const sendButton = document.createElement('button');
        sendButton.className = 'button _button_g7qox_351 _primary_g7qox_611 _medium_g7qox_579 _disabled_g7qox_402';
        sendButton.id = 'send-button';
        sendButton.disabled = true;
        sendButton.setAttribute('aria-disabled', 'true');
        sendButton.setAttribute('aria-live', 'polite');
        sendButton.onclick = sendChatMessage;
        sendButton.textContent = 'Send';
        sendButton.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: white;
            padding: 8px 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 80px;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
        `;
        
        // Add hover and disabled states
        sendButton.addEventListener('mouseenter', () => {
            if (!sendButton.disabled) {
                sendButton.style.transform = 'translateY(-1px)';
                sendButton.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.3)';
            }
        });
        
        sendButton.addEventListener('mouseleave', () => {
            sendButton.style.transform = 'translateY(0)';
            sendButton.style.boxShadow = '0 2px 4px rgba(102, 126, 234, 0.2)';
        });
        
        // Add input event listener to update send button state
        textarea.addEventListener('input', () => {
          updateSendButtonState(textarea, sendButton);
          chatMessage.value = textarea.value;
          
          // Update button appearance based on state
          if (textarea.value.trim()) {
              sendButton.disabled = false;
              sendButton.style.opacity = '1';
              sendButton.style.cursor = 'pointer';
              sendButton.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
          } else {
              sendButton.disabled = true;
              sendButton.style.opacity = '0.5';
              sendButton.style.cursor = 'not-allowed';
              sendButton.style.background = '#9ca3af';
          }
        });
        
        sendButtonContainer.appendChild(sendButton);
        
        // Assemble input container
        inputContainer.appendChild(textareaContainer);
        inputContainer.appendChild(sendButtonContainer);
        
        // Assemble chat controls
        chatControls.appendChild(inputContainer);
        
        // Assemble chat content
        chatContent.appendChild(chatHeader);
        chatContent.appendChild(chatHistory);
        chatContent.appendChild(chatControls);
        
        // Assemble new element
        newElement.appendChild(chatToggle);
        newElement.appendChild(chatContent);
        
        // Append the new element to the sidebar
        sidebar.appendChild(newElement);
    } else {
        console.error("Sidebar div not found!");
    }
}

function waitForSidebar(callback) {
  const sidebar = document.getElementById('sidebar');
  
  // If sidebar already exists, run callback immediately
  if (sidebar) {
    callback();
    return;
  }

  // Otherwise, observe DOM changes
  const observer = new MutationObserver(function(mutations, obs) {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
      callback();
      obs.disconnect(); // Stop observing once found
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}


// Wait for DOM to be ready, then wait for #sidebar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    waitForSidebar(initializeChat);
  });
} else {
  waitForSidebar(initializeChat);
}
