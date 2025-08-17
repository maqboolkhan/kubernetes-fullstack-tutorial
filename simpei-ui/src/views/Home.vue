<template>
  <div class="home">
    <div class="hero">
      <h1 class="hero-title">Welcome to Simpei Todo</h1>
      <p class="hero-subtitle">A simple and elegant todo list application</p>
      <div class="hero-actions">
        <router-link to="/todos" class="btn btn-primary btn-large">
          Get Started
        </router-link>
      </div>
    </div>

    <div class="features">
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">✨</div>
          <h3>Simple & Clean</h3>
          <p>Intuitive interface designed for productivity</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🚀</div>
          <h3>Fast & Reliable</h3>
          <p>Built with modern technologies for optimal performance</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📱</div>
          <h3>Responsive Design</h3>
          <p>Works perfectly on desktop, tablet, and mobile devices</p>
        </div>
      </div>
    </div>

    <div class="api-status">
      <div class="card">
        <h3>API Connection Status</h3>
        <div v-if="loading" class="loading">
          Checking connection...
        </div>
        <div v-else-if="apiStatus.connected" class="success">
          ✅ Connected to Simpei API
          <p><strong>Message:</strong> {{ apiStatus.message }}</p>
        </div>
        <div v-else class="error">
          ❌ Failed to connect to API
          <p><strong>Error:</strong> {{ apiStatus.error }}</p>
          <button @click="checkApiConnection" class="btn btn-secondary">
            Retry Connection
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { todoApi } from '../services/api'

export default {
  name: 'Home',
  data() {
    return {
      loading: true,
      apiStatus: {
        connected: false,
        message: '',
        error: ''
      }
    }
  },
  async mounted() {
    await this.checkApiConnection()
  },
  methods: {
    async checkApiConnection() {
      this.loading = true
      try {
        const response = await todoApi.testConnection()
        this.apiStatus = {
          connected: true,
          message: response.message,
          error: ''
        }
      } catch (error) {
        this.apiStatus = {
          connected: false,
          message: '',
          error: error.message || 'Unknown error occurred'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 3rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions {
  margin-top: 2rem;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.features {
  margin-bottom: 3rem;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.api-status {
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>