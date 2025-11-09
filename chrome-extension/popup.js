// Popup script for the extension

document.addEventListener('DOMContentLoaded', () => {
  const openPlayerBtn = document.getElementById('open-player');
  const statusDiv = document.getElementById('status');
  
  openPlayerBtn.addEventListener('click', async () => {
    try {
      // Get current active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (tab.url && tab.url.includes('booking.com')) {
        // Inject content script if not already injected
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });
        
        // Inject CSS
        await chrome.scripting.insertCSS({
          target: { tabId: tab.id },
          files: ['content.css']
        });
        
        statusDiv.textContent = 'Music player opened!';
        statusDiv.style.display = 'block';
        statusDiv.style.background = '#e8f5e9';
        statusDiv.style.color = '#1DB954';
      } else {
        statusDiv.textContent = 'Please navigate to booking.com first';
        statusDiv.style.display = 'block';
        statusDiv.style.background = '#ffebee';
        statusDiv.style.color = '#d32f2f';
      }
    } catch (error) {
      console.error('Error:', error);
      statusDiv.textContent = 'Error: ' + error.message;
      statusDiv.style.display = 'block';
      statusDiv.style.background = '#ffebee';
      statusDiv.style.color = '#d32f2f';
    }
  });
});

