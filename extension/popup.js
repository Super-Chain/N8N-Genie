// Popup script for N8N Genie extension
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a valid N8N page
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentTab = tabs[0];
        const url = currentTab.url;
        
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const statusDesc = document.getElementById('statusDesc');
        const apiServer = document.getElementById('apiServer');
        
        // Check if current page is an N8N page
        const isN8NPage = url.includes('/workflow') || 
                         url.includes('/workflows') || 
                         url.includes('n8n.cloud') || 
                         url.includes('n8n.io') ||
                         (url.includes('localhost') && (url.includes('5678') || url.includes('3000')));
        
        if (isN8NPage) {
            statusDot.className = 'status-dot active';
            statusText.textContent = 'Active on this page';
            statusDesc.textContent = 'The AI assistant is ready to help with your N8N workflows.';
        } else {
            statusDot.className = 'status-dot inactive';
            statusText.textContent = 'Not an N8N page';
            statusDesc.textContent = 'Navigate to an N8N workflow page to use the AI assistant.';
        }
        
        // Update API server info based on environment
        if (url.includes('localhost') || url.includes('127.0.0.1')) {
            apiServer.textContent = 'localhost:1234';
        } else {
            apiServer.textContent = 'localhost:1234';
        }
    });
    
    // Add click handler for future settings if needed
    document.addEventListener('click', function(e) {
        if (e.target.id === 'openSettings') {
            chrome.runtime.openOptionsPage();
        }
    });
});