// Generate a UUID v4 - simple implementation
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    let r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Retrieve or create session ID for persistent tracking
let sessionId = localStorage.getItem('session_id');
if (!sessionId) {
  sessionId = generateUUID();
  localStorage.setItem('session_id', sessionId);
}

// Replace or assign user ID if you have logged-in user info
const userId = null;

// Event logging function
function logEvent(eventType, properties = {}) {
  const eventPayload = {
    event_id: generateUUID(),
    event_type: eventType,
    user_id: userId,
    session_id: sessionId,
    timestamp: new Date().toISOString(),
    properties: properties
  };

  fetch('http://localhost:8001/events', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(eventPayload),
  }).catch(console.error);
}

// Track page load
window.addEventListener('load', () => {
  logEvent('page_load', { page: window.location.pathname });
});

// Track button clicks globally for buttons with ID attribute
document.addEventListener('click', (event) => {
  if (event.target.tagName === 'BUTTON') {
    logEvent('button_click', {
      button_id: event.target.id || event.target.innerText,
      page_url: window.location.href
    });
  }
});
