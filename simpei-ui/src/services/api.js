import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Todo API methods
export const todoApi = {
  // Get all todos
  async getTodos(skip = 0, limit = 100) {
    const response = await api.get('/todos/', {
      params: { skip, limit }
    })
    return response.data
  },

  // Get todo by ID
  async getTodo(id) {
    const response = await api.get(`/todos/${id}`)
    return response.data
  },

  // Create new todo
  async createTodo(todo) {
    const response = await api.post('/todos/', todo)
    return response.data
  },

  // Update todo
  async updateTodo(id, updates) {
    const response = await api.put(`/todos/${id}`, updates)
    return response.data
  },

  // Delete todo
  async deleteTodo(id) {
    await api.delete(`/todos/${id}`)
  },

  // Get todos by completion status
  async getTodosByStatus(completed) {
    const response = await api.get(`/todos/completed/${completed}`)
    return response.data
  },

  // Test API connection
  async testConnection() {
    const response = await api.get('/')
    return response.data
  }
}

export default api