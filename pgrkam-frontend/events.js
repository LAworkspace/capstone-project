// Place in your static site JS bundle
function logEvent(eventType, metadata = {}) {
  fetch("http://localhost:8000/api/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: "user_123",
      session_id: "session_abc",
      event_type: eventType,
      timestamp: new Date().toISOString(),
      metadata,
    }),
  });
}

// Example usage
window.addEventListener("load", () => logEvent("page_load", { page: window.location.pathname }));
document.getElementById("apply_button").addEventListener("click", () =>
  logEvent("click", { button: "apply" })
);
