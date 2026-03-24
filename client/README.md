# God is with You

A responsive web application that displays daily verses and provides personalized messages based on user input.

## Tech Stack

- **Frontend**: React 18 + Vite
- **Styling**: Tailwind CSS v4
- **Language**: JavaScript (ES6+)
- **Build Tool**: Vite
- **Package Manager**: npm

## Features

- **Daily Verse Display**: Fetches and displays daily Bible verses or messages
- **Custom Message Input**: Users can submit text to receive personalized messages
- **Language Selection**: Toggle between Korean (KR) and English (EN)
- **Persistent Language Settings**: Language preference saved to localStorage
- **Responsive Design**: Optimized for desktop and mobile devices
- **Loading Animation**: Smooth pulsing animation during data fetching
- **Dynamic Enter Key Behavior**: 
  - PC: Enter sends, Shift+Enter wraps
  - Mobile: Enter creates new line

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Server runs at `http://localhost:5173` by default.

## Build

```bash
npm run build
```

## Environment Variables

Create a `.env` file in the project root:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
src/
├── App.jsx              # Main app component with routing
├── main.jsx             # Entry point
├── api/
│   └── bibleApi.js      # API integration
├── components/
│   ├── ChatInput.jsx    # Text input with auto-resize
│   ├── VerseDisplay.jsx # Verse rendering
│   └── LanguageSelector.jsx # Language toggle
└── styles/
    └── index.css        # Global styles and animations
```

## API Endpoints

**Base URL**: `{VITE_API_BASE_URL}/api/v1`

- `GET /daily-verse?language=<language>` - Fetch daily verse
- `POST /custom-message?language=<language>` - Submit custom message request

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
