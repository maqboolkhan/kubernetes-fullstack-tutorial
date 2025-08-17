<template>
  <div class="todo-list">
    <div class="header">
      <h1>My Todos</h1>
      <div class="header-actions">
        <div class="filter-buttons">
          <button 
            @click="setFilter('all')" 
            :class="['btn', 'btn-secondary', { 'active': currentFilter === 'all' }]"
          >
            All ({{ todos.length }})
          </button>
          <button 
            @click="setFilter('active')" 
            :class="['btn', 'btn-secondary', { 'active': currentFilter === 'active' }]"
          >
            Active ({{ activeTodos.length }})
          </button>
          <button 
            @click="setFilter('completed')" 
            :class="['btn', 'btn-secondary', { 'active': currentFilter === 'completed' }]"
          >
            Completed ({{ completedTodos.length }})
          </button>
        </div>
      </div>
    </div>

    <!-- Add Todo Form -->
    <div class="card">
      <h3>Add New Todo</h3>
      <form @submit.prevent="addTodo" class="todo-form">
        <div class="form-group">
          <label for="title" class="form-label">Title *</label>
          <input
            id="title"
            v-model="newTodo.title"
            type="text"
            class="form-input"
            placeholder="Enter todo title..."
            required
          />
        </div>
        <div class="form-group">
          <label for="description" class="form-label">Description</label>
          <textarea
            id="description"
            v-model="newTodo.description"
            class="form-textarea"
            placeholder="Enter todo description (optional)..."
          ></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Adding...' : 'Add Todo' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Error/Success Messages -->
    <div v-if="error" class="error">
      {{ error }}
    </div>
    <div v-if="successMessage" class="success">
      {{ successMessage }}
    </div>

    <!-- Loading State -->
    <div v-if="loading && todos.length === 0" class="loading">
      Loading todos...
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTodos.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>{{ getEmptyStateMessage() }}</h3>
      <p v-if="currentFilter === 'all'">Start by adding your first todo above!</p>
    </div>

    <!-- Todo Items -->
    <div v-else class="todos-container">
      <div 
        v-for="todo in filteredTodos" 
        :key="todo.id" 
        :class="['todo-item', { 'completed': todo.completed }]"
      >
        <div class="todo-content">
          <div class="todo-header">
            <div class="checkbox-group">
              <input
                type="checkbox"
                :checked="todo.completed"
                @change="toggleTodo(todo)"
                class="checkbox-input"
              />
              <h4 :class="['todo-title', { 'completed': todo.completed }]">
                {{ todo.title }}
              </h4>
            </div>
            <div class="todo-actions">
              <button @click="editTodo(todo)" class="btn btn-sm btn-secondary">
                Edit
              </button>
              <button @click="deleteTodo(todo.id)" class="btn btn-sm btn-danger">
                Delete
              </button>
            </div>
          </div>
          <p v-if="todo.description" class="todo-description">
            {{ todo.description }}
          </p>
          <div class="todo-meta">
            <small class="todo-date">
              Created: {{ formatDate(todo.created_at) }}
            </small>
            <small v-if="todo.updated_at" class="todo-date">
              Updated: {{ formatDate(todo.updated_at) }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingTodo" class="modal-overlay" @click="cancelEdit">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Edit Todo</h3>
          <button @click="cancelEdit" class="btn btn-secondary">×</button>
        </div>
        <form @submit.prevent="updateTodo" class="modal-body">
          <div class="form-group">
            <label for="edit-title" class="form-label">Title *</label>
            <input
              id="edit-title"
              v-model="editForm.title"
              type="text"
              class="form-input"
              required
            />
          </div>
          <div class="form-group">
            <label for="edit-description" class="form-label">Description</label>
            <textarea
              id="edit-description"
              v-model="editForm.description"
              class="form-textarea"
            ></textarea>
          </div>
          <div class="checkbox-group">
            <input
              id="edit-completed"
              v-model="editForm.completed"
              type="checkbox"
              class="checkbox-input"
            />
            <label for="edit-completed" class="form-label">Completed</label>
          </div>
          <div class="modal-actions">
            <button type="button" @click="cancelEdit" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Updating...' : 'Update Todo' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { todoApi } from '../services/api'

export default {
  name: 'TodoList',
  data() {
    return {
      todos: [],
      loading: false,
      error: '',
      successMessage: '',
      currentFilter: 'all',
      newTodo: {
        title: '',
        description: '',
        completed: false
      },
      editingTodo: null,
      editForm: {
        title: '',
        description: '',
        completed: false
      }
    }
  },
  computed: {
    activeTodos() {
      return this.todos.filter(todo => !todo.completed)
    },
    completedTodos() {
      return this.todos.filter(todo => todo.completed)
    },
    filteredTodos() {
      switch (this.currentFilter) {
        case 'active':
          return this.activeTodos
        case 'completed':
          return this.completedTodos
        default:
          return this.todos
      }
    }
  },
  async mounted() {
    await this.fetchTodos()
  },
  methods: {
    async fetchTodos() {
      this.loading = true
      this.error = ''
      try {
        this.todos = await todoApi.getTodos()
      } catch (error) {
        this.error = `Failed to fetch todos: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    async addTodo() {
      if (!this.newTodo.title.trim()) return

      this.loading = true
      this.error = ''
      this.successMessage = ''
      
      try {
        const todo = await todoApi.createTodo({
          title: this.newTodo.title.trim(),
          description: this.newTodo.description.trim() || null,
          completed: false
        })
        
        this.todos.unshift(todo)
        this.newTodo = { title: '', description: '', completed: false }
        this.successMessage = 'Todo added successfully!'
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
      } catch (error) {
        this.error = `Failed to add todo: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    async toggleTodo(todo) {
      try {
        const updated = await todoApi.updateTodo(todo.id, {
          completed: !todo.completed
        })
        
        const index = this.todos.findIndex(t => t.id === todo.id)
        if (index !== -1) {
          this.todos.splice(index, 1, updated)
        }
      } catch (error) {
        this.error = `Failed to update todo: ${error.message}`
      }
    },

    editTodo(todo) {
      this.editingTodo = todo
      this.editForm = {
        title: todo.title,
        description: todo.description || '',
        completed: todo.completed
      }
    },

    async updateTodo() {
      if (!this.editForm.title.trim()) return

      this.loading = true
      this.error = ''
      
      try {
        const updated = await todoApi.updateTodo(this.editingTodo.id, {
          title: this.editForm.title.trim(),
          description: this.editForm.description.trim() || null,
          completed: this.editForm.completed
        })
        
        const index = this.todos.findIndex(t => t.id === this.editingTodo.id)
        if (index !== -1) {
          this.todos.splice(index, 1, updated)
        }
        
        this.cancelEdit()
        this.successMessage = 'Todo updated successfully!'
        
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
      } catch (error) {
        this.error = `Failed to update todo: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    async deleteTodo(id) {
      if (!confirm('Are you sure you want to delete this todo?')) return

      try {
        await todoApi.deleteTodo(id)
        this.todos = this.todos.filter(todo => todo.id !== id)
        this.successMessage = 'Todo deleted successfully!'
        
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
      } catch (error) {
        this.error = `Failed to delete todo: ${error.message}`
      }
    },

    cancelEdit() {
      this.editingTodo = null
      this.editForm = { title: '', description: '', completed: false }
    },

    setFilter(filter) {
      this.currentFilter = filter
    },

    getEmptyStateMessage() {
      switch (this.currentFilter) {
        case 'active':
          return 'No active todos'
        case 'completed':
          return 'No completed todos'
        default:
          return 'No todos yet'
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header h1 {
  color: #333;
  font-size: 2rem;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
}

.filter-buttons .btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.todo-form {
  display: grid;
  gap: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.todos-container {
  display: grid;
  gap: 1rem;
}

.todo-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #667eea;
}

.todo-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.todo-item.completed {
  opacity: 0.7;
  border-left-color: #28a745;
}

.todo-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.todo-title {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.todo-title.completed {
  text-decoration: line-through;
  color: #666;
}

.todo-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.todo-description {
  color: #666;
  margin: 0.5rem 0;
  line-height: 1.5;
}

.todo-meta {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.todo-date {
  color: #999;
  font-size: 0.85rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.modal-body {
  padding: 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-buttons {
    justify-content: center;
  }
  
  .todo-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .todo-actions {
    justify-content: flex-start;
  }
  
  .modal {
    width: 95%;
    margin: 1rem;
  }
}
</style>