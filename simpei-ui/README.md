# Simpei UI

A modern Vue.js frontend for the Simpei Todo application. This is a responsive web interface that provides a clean and intuitive way to manage your todos.

## Features

- 📝 Create, read, update, and delete todos
- ✅ Mark todos as complete/incomplete
- 🎨 Modern, responsive design with gradient styling
- 🔄 Real-time API integration
- 📱 Mobile-friendly interface
- 🚀 Fast development with Vue 3 and Vue CLI

## Tech Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router 4** - Client-side routing
- **Axios** - HTTP client for API requests
- **Vue CLI 5** - Development tooling
- **ESLint** - Code linting with Standard config

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager

## Installation

1. Navigate to the project directory:
```bash
cd simpei-ui
```

2. Install dependencies:
```bash
npm install
```

## Development

### Start the development server:
```bash
npm run serve
# or
npm run dev
```

The application will be available at `http://localhost:3000`

### Other available commands:

- **Build for production:**
  ```bash
  npm run build
  ```

- **Lint and fix files:**
  ```bash
  npm run lint
  ```

## Configuration

### Environment Variables

The application uses environment variables defined in `.env`:

- `VUE_APP_API_URL` - Backend API URL (default: `/api`)
- `VUE_APP_TITLE` - Application title

### API Integration

The frontend communicates with the Simpei backend API through the following endpoints:

- `GET /api/todos` - Fetch all todos
- `POST /api/todos` - Create a new todo
- `GET /api/todos/:id` - Get a specific todo
- `PUT /api/todos/:id` - Update a todo
- `DELETE /api/todos/:id` - Delete a todo
- `GET /api/todos/status/:completed` - Get todos by completion status

## Project Structure

```
simpei-ui/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # Reusable Vue components
│   ├── views/             # Page components
│   │   ├── Home.vue       # Home page
│   │   └── TodoList.vue   # Todo management page
│   ├── router/
│   │   └── index.js       # Vue Router configuration
│   ├── services/
│   │   └── api.js         # API service layer
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── .env                   # Environment variables
├── package.json           # Dependencies and scripts
└── vue.config.js          # Vue CLI configuration
```

## Deployment

### Docker

The project includes a Dockerfile for containerized deployment:

```bash
docker build -t simpei-ui .
docker run -p 80:80 simpei-ui
```

### Production Build

For production deployment:

1. Build the application:
   ```bash
   npm run build
   ```

2. Serve the `dist/` directory with a web server like nginx


