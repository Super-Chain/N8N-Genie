const fs = require('fs');
const path = require('path');

function addLineToFile(filePath, newLine) {
	try {
		// Read the existing content of the file
		let content = '';
		if (fs.existsSync(filePath)) {
			content = fs.readFileSync(filePath, 'utf8');
		}
		
		// Add the new line (ensure there's a newline character if content exists)
		if (content && !content.endsWith('\n')) {
			content += '\n';
		}
		// Find the position of </head> and insert the new line before it
		const headCloseTag = '</head>';
		const headIndex = content.indexOf(headCloseTag);
		
		if (headIndex !== -1) {
			// Insert the new line before </head>
			content = content.slice(0, headIndex) + newLine + '\n\t\t' + content.slice(headIndex);
		} else {
			// If </head> is not found, append to the end as fallback
			content += newLine + '\n';
		}
		
		// Write the updated content back to the file
		fs.writeFileSync(filePath, content, 'utf8');
		
		console.log(`Successfully added line to ${filePath}`);
		return true;
	} catch (error) {
		console.error(`Error processing file ${filePath}:`, error.message);
		return false;
	}
}

// Add plugin script to HTML
addLineToFile(
    '/usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/dist/index.html', 
    '	<script type="module" crossorigin src="/{{BASE_PATH}}/assets/plugin.js"></script>'
);






