# Spoon Feedr Web UI Customization (Zhipu Aesthetic)

To achieve the Zhipu-style high-end aesthetic in Open WebUI or LibreChat, follow these steps:

## 1. Custom CSS (Inject into Open WebUI)

```css
:root {
  --background-chat: #f7f9fb;
  --text-primary: #1a1a1a;
  --accent-color: #2b57ff;
  --border-radius: 12px;
}

.chat-container {
  font-family: 'Inter', sans-serif;
  background-color: var(--background-chat);
}

.message-user {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: var(--border-radius);
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.message-bot {
  background: transparent;
}

.sidebar {
  background: #ffffff;
  border-right: 1px solid #eef2f6;
}
```

## 2. API Integration

Point your Open WebUI or custom React frontend to the Spoon Feedr FastAPI backend:
- Endpoint: `http://localhost:8000/chat`

## 3. Telemetry Sidebar Component (React Snippet)

```jsx
const TelemetrySidebar = ({ events }) => {
  return (
    <div className="p-4 bg-white border-l h-full">
      <h3 className="text-sm font-bold uppercase text-gray-500 mb-4">Live Agents</h3>
      {events.map((event, i) => (
        <div key={i} className="mb-2 text-xs font-mono p-2 bg-gray-50 rounded">
          {JSON.stringify(event)}
        </div>
      ))}
    </div>
  );
}
```
