# 🧞‍♂️ N8N Genie - Chrome Extension

> Your AI-Powered N8N Workflow Assistant - No coding knowledge required!

N8N Genie is a Chrome extension that adds an intelligent AI assistant directly to your N8N workflow editor. Get instant help creating, debugging, and optimizing your workflows through natural conversation.

## ✨ Features

- 🤖 **AI-Powered Assistance** - Smart workflow suggestions and debugging help
- 💬 **Natural Chat Interface** - Talk to your AI assistant in plain English
- ⚡ **Instant Integration** - Works seamlessly with any N8N instance
- 🔧 **No Setup Required** - Just install and start chatting
- 🌐 **Universal Compatibility** - Works with localhost, n8n.cloud, and self-hosted instances

## 🚀 Quick Installation (2 Minutes)

### Step 1: Download
Download this entire `n8n-genie-js` folder to your computer.

### Step 2: Open Chrome Extensions
- Open Google Chrome
- Type `chrome://extensions/` in the address bar and press Enter
- OR click the three dots menu (⋮) → More tools → Extensions

### Step 3: Enable Developer Mode
- Toggle ON the "Developer mode" switch in the top-right corner

### Step 4: Install Extension
- Click "Load unpacked" button
- Select the `n8n-genie-js` folder you downloaded

### Step 5: Start Using!
- Go to any N8N workflow page
- Look for the chat toggle button on the right side
- Click to open the AI assistant and start chatting!

## 📋 System Requirements

- **Browser**: Google Chrome (version 88+) or Chromium-based browsers
- **N8N**: Any version (localhost, cloud, or self-hosted)
- **API Server**: Localhost:1234 (included with N8N Genie backend)

## 🎯 How to Use

1. **Open N8N**: Navigate to any workflow in your N8N instance
2. **Find the Chat**: Look for the genie icon (🧞‍♂️) on the right side of your screen
3. **Start Chatting**: Click the chat toggle and describe what you want to build
4. **Get Help**: Ask questions like:
   - "Create a workflow to send Slack notifications"
   - "Debug my HTTP request node"
   - "How do I connect to a database?"
   - "Optimize this workflow for better performance"

## 🛠️ Troubleshooting

### Extension not showing up?
- ✅ Make sure Developer mode is enabled
- ✅ Check that the extension appears in `chrome://extensions/`
- ✅ Try disabling and re-enabling the extension

### Chat toggle not visible?
- ✅ Ensure you're on a workflow page (URL contains `/workflow` or `/workflows`)
- ✅ Refresh the page after installing
- ✅ Check browser console (F12) for any errors

### AI not responding?
- ✅ Verify your API server is running on localhost:1234
- ✅ Check your internet connection
- ✅ Look at browser console (F12) for error messages

### Using self-hosted N8N?
- ✅ The extension works with any N8N instance
- ✅ Make sure your N8N page URL matches the patterns in the manifest
- ✅ Custom domains are supported

## 🔧 Technical Details

### Files Included
- `manifest.json` - Extension configuration
- `plugin.js` - Main extension functionality  
- `popup.html` - Extension popup interface
- `popup.js` - Popup functionality
- `install-instructions.html` - Detailed installation guide

### Permissions
- `activeTab` - To interact with N8N pages
- `storage` - To save user preferences
- `host_permissions` - To work with various N8N instances

### Supported URLs
- `*://*/workflow/*` - Standard workflow pages
- `*://*/workflows/*` - Workflow listing pages
- `*://localhost:*/*` - Local N8N instances
- `*://*.n8n.cloud/*` - N8N Cloud instances
- `*://*.n8n.io/*` - Official N8N instances

## 🎨 Customization

The extension automatically adapts to your N8N theme and integrates seamlessly with the existing interface. The chat sidebar respects N8N's design system and color scheme.

## 🤝 Support

Having issues? Here are some helpful resources:

- 📖 **Installation Guide**: Open `install-instructions.html` for detailed steps with screenshots
- 🐛 **Bug Reports**: Check browser console (F12) for error messages
- 💡 **Feature Requests**: The extension is actively developed and improved

## 📱 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Fully Supported | Recommended browser |
| Edge | ✅ Supported | Chromium-based |
| Opera | ✅ Supported | Chromium-based |
| Firefox | ❌ Not Supported | Uses different extension format |
| Safari | ❌ Not Supported | Uses different extension format |

## 🔒 Privacy & Security

- 🔐 **Local Processing**: Your workflow data stays in your browser
- 🌐 **Secure Communication**: All API calls use HTTPS when possible  
- 🚫 **No Data Collection**: The extension doesn't collect or store personal data
- 🛡️ **Open Source**: Full transparency in functionality

## 📦 What's Next?

After installation, you can:
- Start building workflows with AI assistance
- Debug existing workflows by describing issues
- Get suggestions for workflow optimization
- Learn N8N best practices through conversation
- Explore advanced automation possibilities

---

**Ready to supercharge your N8N workflows?** Install the extension and start chatting with your AI assistant today! 🚀