# Jenkins Agent Dashboard

A simple HTML/CSS/JavaScript dashboard for monitoring Jenkins Agent builds and AI analysis.

## Features

- **📊 Real-time Statistics**: Success/failure rates, total builds, retry counts
- **🔍 Build Filtering**: Filter by status and search by job name or build number
- **🧠 AI Analysis Display**: Shows LLM failure analysis and success recommendations
- **📋 Detailed Build View**: Modal with complete build information, logs, and Jenkinsfile
- **⚡ Auto-refresh**: Updates every 30 seconds automatically
- **📱 Responsive Design**: Works on desktop and mobile devices

## Structure

```
dashboard/
├── index.html      # Main dashboard page
├── styles.css      # Styling and responsive design
├── script.js       # JavaScript functionality
└── README.md       # This file
```

## Usage

1. Start the AI Agents API server:
   ```bash
   python src/ai_agents/deployment/api_agent/start_api.py
   ```

2. Access the dashboard:
   ```
   http://localhost:8000/dashboard
   ```

## API Integration

The dashboard connects to these API endpoints:
- `GET /api/agents/jenkins_agent/runs` - Fetch all build runs
- Real-time updates every 30 seconds

## Data Structure

The dashboard displays data from Jenkins webhook executions including:

### Build Information
- Job name and build number
- Build status (SUCCESS/FAILURE)
- Start/completion times and duration
- Agent execution status

### AI Analysis
- **Failure Analysis**: Root cause, category, confidence, suggested actions
- **Success Analysis**: Summary, improvements, confidence
- **Decision Making**: Retry logic, action taken

### Logs and Code
- Jenkins console logs (sanitized)
- Jenkinsfile content
- Agent execution logs

## Customization

### Styling
Edit `styles.css` to customize:
- Colors and theme
- Card layouts
- Responsive breakpoints
- Animations and transitions

### Functionality
Edit `script.js` to modify:
- API endpoints
- Refresh intervals
- Filtering logic
- Modal content

### Layout
Edit `index.html` to change:
- Page structure
- Statistics cards
- Filter controls
- Modal layout

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

## Performance

- Lightweight vanilla JavaScript (no frameworks)
- Efficient DOM updates
- CSS animations with hardware acceleration
- Responsive image and content loading
