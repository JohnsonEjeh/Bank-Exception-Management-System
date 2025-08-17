<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from './api'

type User = { 
  id: number
  username: string
  email: string
  full_name?: string | null
  is_active: boolean 
}

type ExceptionType = { 
  id: number
  code: string
  name: string 
}

type Exception = {
  id: number
  type_id: number
  title: string
  severity?: string | null
  priority?: number | null
}

type AttachmentListItem = {
  id: number
  filename: string
  mime?: string | null
  uploaded_by?: number | null
  uploaded_at?: string | null
  size?: number | null
etag?: string | null
}

const users = ref<User[]>([])
const types = ref<ExceptionType[]>([])
const exList = ref<Exception[]>([])

const newUser = ref<{ username: string; email: string; full_name?: string }>({ 
  username: '', 
  email: '', 
  full_name: '' 
})

const newType = ref<{ 
  code: string
  name: string
  description?: string
  default_sla_hours: number
  approval_levels: number
  active: boolean 
}>({
  code: '', 
  name: '', 
  description: '', 
  default_sla_hours: 48, 
  approval_levels: 1, 
  active: true
})

const newException = ref<{ 
  type_id: number | null
  title: string
  severity: string
  priority: number | null 
}>({
  type_id: null, 
  title: '', 
  severity: 'HIGH', 
  priority: 1
})

const selectedExceptionId = ref<number | null>(null)
const attachments = ref<AttachmentListItem[]>([])
const fileInput = ref<HTMLInputElement | null>(null)
const message = ref('')
const isLoading = ref(false)

async function refreshAll() {
  try {
    isLoading.value = true
    users.value = await api<User[]>('/users')
    types.value = await api<ExceptionType[]>('/exception-types')
    exList.value = await api<Exception[]>('/exceptions')
  } catch (error) {
    message.value = `Error loading data: ${error}`
  } finally {
    isLoading.value = false
  }
}

async function createUser() {
  try {
    isLoading.value = true
    const out = await api<User>('/users', { 
      method: 'POST', 
      body: JSON.stringify(newUser.value) 
    })
    message.value = `✅ User created successfully (ID: ${out.id})`
    newUser.value = { username: '', email: '', full_name: '' }
    await refreshAll()
  } catch (error) {
    message.value = `❌ Error creating user: ${error}`
  } finally {
    isLoading.value = false
  }
}

async function createType() {
  try {
    isLoading.value = true
    const body = { ...newType.value }
    const out = await api<ExceptionType>('/exception-types', { 
      method: 'POST', 
      body: JSON.stringify(body) 
    })
    message.value = `✅ Exception type created successfully (ID: ${out.id})`
    newType.value = {
      code: '', 
      name: '', 
      description: '', 
      default_sla_hours: 48, 
      approval_levels: 1, 
      active: true
    }
    await refreshAll()
  } catch (error) {
    message.value = `❌ Error creating type: ${error}`
  } finally {
    isLoading.value = false
  }
}

async function createException() {
  const { type_id } = newException.value
  if (!type_id) { 
    message.value = '⚠️ Please select an exception type'
    return 
  }

  try {
    isLoading.value = true
    const body = { ...newException.value, type_id: Number(type_id) }
    const out = await api<Exception>('/exceptions', { 
      method: 'POST', 
      body: JSON.stringify(body) 
    })
    message.value = `✅ Exception created successfully (ID: ${out.id})`
    selectedExceptionId.value = out.id
    newException.value = { type_id: null, title: '', severity: 'HIGH', priority: 1 }
    await refreshAll()
    await loadAttachments()
  } catch (error) {
    message.value = `❌ Error creating exception: ${error}`
  } finally {
    isLoading.value = false
  }
}

async function loadAttachments() {
  if (!selectedExceptionId.value) { 
    attachments.value = []
    return 
  }

  try {
    attachments.value = await api<AttachmentListItem[]>(`/attachments/by-exception/${selectedExceptionId.value}`)
  } catch (error) {
    message.value = `❌ Error loading attachments: ${error}`
  }
}

async function uploadFile() {
  const f = fileInput.value?.files?.[0]
  if (!f || !selectedExceptionId.value) { 
    message.value = '⚠️ Please select a file and an exception'
    return 
  }

  try {
    isLoading.value = true
    const presign = await api<{ attachment_id: number; upload_url: string; key: string }>('/attachments/presign-upload', {
      method: 'POST',
      body: JSON.stringify({
        exception_id: selectedExceptionId.value,
        filename: f.name,
        mime: f.type || 'application/octet-stream',
        uploaded_by: users.value[0]?.id ?? null
      })
    })

    const putRes = await fetch(presign.upload_url, {
      method: 'PUT',
      headers: { 'Content-Type': f.type || 'application/octet-stream' },
      body: f
    })

    if (!putRes.ok) {
      throw new Error(`Upload failed: ${putRes.status} ${putRes.statusText}`)
    }
    await api('/attachments/finalize', {
      method: 'POST',
      body: JSON.stringify({ attachment_id: presign.attachment_id })
    })

    message.value = `✅ Successfully uploaded ${f.name}`
    if (fileInput.value) fileInput.value.value = ''
    await loadAttachments()
  } catch (error) {
    message.value = `❌ Upload failed: ${error}`
  } finally {
    isLoading.value = false
  }
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'Unknown'
  return new Date(dateStr).toLocaleString()
}

async function downloadAttachment(id: number) {
  try {
    const out = await api<{ download_url: string }>('/attachments/presign-download', {
      method: 'POST',
      body: JSON.stringify({ attachment_id: id })
    })
    window.open(out.download_url, '_blank')
  } catch (e) {
    message.value = `❌ Download failed: ${e}`
  }
}


function formatBytes(n?: number | null): string {
  if (!n && n !== 0) return ''
  const units = ['B','KB','MB','GB','TB']
  let i = 0
  let v = n
  while (v >= 1024 && i < units.length - 1) { v = v / 1024; i++ }
  return `${v.toFixed(v < 10 && i > 0 ? 1 : 0)} ${units[i]}`
}

onMounted(refreshAll)
</script>

<template>
  <main class="admin-container">
    <header class="header">
      <h1 class="title">
        <span class="icon">⚙️</span>
        Exception Management System
      </h1>
      <div class="subtitle">Administration Panel</div>
    </header>

    <div v-if="message" class="message-bar" :class="{
      'success': message.includes('✅'),
      'error': message.includes('❌'),
      'warning': message.includes('⚠️')
    }">
      {{ message }}
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>Processing...</span>
    </div>

    <div class="grid-container">
      <!-- Create User Section -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">
            <span class="card-icon">👤</span>
            Create User
          </h2>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">Username *</label>
            <input 
              v-model="newUser.username" 
              class="form-input" 
              placeholder="Enter username"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">Email *</label>
            <input 
              v-model="newUser.email" 
              type="email"
              class="form-input" 
              placeholder="user@example.com"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input 
              v-model="newUser.full_name" 
              class="form-input" 
              placeholder="John Doe"
            />
          </div>
          <button 
            @click="createUser" 
            class="btn btn-primary"
            :disabled="isLoading || !newUser.username || !newUser.email"
          >
            Create User
          </button>
          <div class="data-summary" v-if="users.length">
            <strong>Users ({{ users.length }}):</strong>
            <div class="tag-container">
              <span 
                v-for="u in users" 
                :key="u.id" 
                class="tag"
                :class="{ 'inactive': !u.is_active }"
              >
                {{ u.username }} (#{{ u.id }})
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Create Exception Type Section -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">
            <span class="card-icon">🏷️</span>
            Create Exception Type
          </h2>
        </div>
        <div class="card-content">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Code *</label>
              <input 
                v-model="newType.code" 
                class="form-input" 
                placeholder="e.g., SYS_ERR"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">Name *</label>
              <input 
                v-model="newType.name" 
                class="form-input" 
                placeholder="System Error"
                required
              />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Description</label>
            <input 
              v-model="newType.description" 
              class="form-input" 
              placeholder="Detailed description..."
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">SLA Hours</label>
              <input 
                type="number" 
                v-model.number="newType.default_sla_hours" 
                class="form-input"
                min="1"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Approval Levels</label>
              <input 
                type="number" 
                v-model.number="newType.approval_levels" 
                class="form-input"
                min="1"
              />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="newType.active" 
                  class="form-checkbox"
                />
                <span class="checkmark"></span>
                Active
              </label>
            </div>
          </div>
          <button 
            @click="createType" 
            class="btn btn-primary"
            :disabled="isLoading || !newType.code || !newType.name"
          >
            Create Type
          </button>
          <div class="data-summary" v-if="types.length">
            <strong>Types ({{ types.length }}):</strong>
            <div class="tag-container">
              <span v-for="t in types" :key="t.id" class="tag">
                {{ t.code }} (#{{ t.id }})
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Create Exception Section -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">
            <span class="card-icon">⚡</span>
            Create Exception
          </h2>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">Exception Type *</label>
            <select 
              v-model.number="newException.type_id" 
              class="form-select"
              required
            >
              <option disabled :value="null">-- Select Type --</option>
              <option v-for="t in types" :key="t.id" :value="t.id">
                {{ t.code }} - {{ t.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Title *</label>
            <input 
              v-model="newException.title" 
              class="form-input" 
              placeholder="Exception title"
              required
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Severity</label>
              <select v-model="newException.severity" class="form-select">
                <option value="LOW" class="severity-low">🟢 LOW</option>
                <option value="MEDIUM" class="severity-medium">🟡 MEDIUM</option>
                <option value="HIGH" class="severity-high">🔴 HIGH</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Priority</label>
              <input 
                type="number" 
                v-model.number="newException.priority" 
                class="form-input"
                min="1"
                max="5"
              />
            </div>
          </div>
          <button 
            @click="createException" 
            class="btn btn-primary"
            :disabled="isLoading || !newException.type_id || !newException.title"
          >
            Create Exception
          </button>
          <div class="data-summary" v-if="exList.length">
            <strong>Exceptions ({{ exList.length }}):</strong>
            <div class="tag-container">
              <span v-for="e in exList" :key="e.id" class="tag">
                {{ e.title }} (#{{ e.id }})
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Attachments Section -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">
            <span class="card-icon">📎</span>
            File Attachments
          </h2>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">Select Exception</label>
            <select 
              v-model.number="selectedExceptionId" 
              @change="loadAttachments"
              class="form-select"
            >
              <option disabled :value="null">-- Select Exception --</option>
              <option v-for="e in exList" :key="e.id" :value="e.id">
                #{{ e.id }} - {{ e.title }}
              </option>
            </select>
          </div>
          <div class="upload-section">
            <div class="file-input-wrapper">
              <input 
                type="file" 
                ref="fileInput" 
                class="file-input"
                id="file-upload"
              />
              <label for="file-upload" class="file-input-label">
                📁 Choose File
              </label>
            </div>
            <button 
              @click="uploadFile" 
              class="btn btn-secondary"
              :disabled="isLoading || !selectedExceptionId"
            >
              Upload File
            </button>
          </div>
          <div class="attachments-list" v-if="attachments.length">
            <h4>Attached Files ({{ attachments.length }})</h4>
            <div class="attachment-item" v-for="a in attachments" :key="a.id">
              <div class="attachment-info">
                <div class="attachment-name">📄 {{ a.filename }}</div>
                <div class="attachment-meta">
                  <span class="attachment-type">{{ a.mime || 'unknown type' }}</span>
                  <span class="attachment-date">{{ formatDate(a.uploaded_at) }}</span>
                  <span class="attachment-type">{{ a.mime || 'unknown type' }}</span>
                  <span v-if="a.size" class="attachment-type">{{ formatBytes(a.size) }}</span>
                  <span v-if="a.etag" class="attachment-type">etag: {{ a.etag.slice(0,8) }}…</span>
                  <span class="attachment-date">{{ formatDate(a.uploaded_at) }}</span>
                </div>
              </div>
              <div style="margin-top:.5rem;">
                <button class="btn btn-secondary" @click="downloadAttachment(a.id)">Download</button>
              </div>
            </div>
          </div>
          <div v-else-if="selectedExceptionId" class="empty-state">
            No files attached to this exception
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.admin-container {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  position: relative;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.icon {
  margin-right: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
}

.message-bar {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #3b82f6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-weight: 500;
}

.message-bar.success {
  border-left-color: #10b981;
  background: #ecfdf5;
  color: #065f46;
}

.message-bar.error {
  border-left-color: #ef4444;
  background: #fef2f2;
  color: #991b1b;
}

.message-bar.warning {
  border-left-color: #f59e0b;
  background: #fffbeb;
  color: #92400e;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 1rem;
  color: white;
  font-size: 1.1rem;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255,255,255,0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.2);
}

.card-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

.card-content {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background: white;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0;
}

.form-checkbox {
  margin-right: 0.5rem;
  transform: scale(1.2);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(107, 114, 128, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.4);
}

.data-summary {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #3b82f6;
  color: white;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.tag.inactive {
  background: #9ca3af;
}

.upload-section {
  display: flex;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1.5rem;
}

.file-input-wrapper {
  flex: 1;
}

.file-input {
  display: none;
}

.file-input-label {
  display: block;
  padding: 0.75rem;
  background: #f3f4f6;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  color: #6b7280;
}

.file-input-label:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.attachments-list h4 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.1rem;
}

.attachment-item {
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.attachment-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.attachment-name {
  font-weight: 600;
  color: #1e293b;
}

.attachment-meta {
  display: flex;
  flex-direction: column;
  align-items: end;
  font-size: 0.8rem;
  color: #6b7280;
}

.attachment-type {
  background: #e2e8f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.25rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  font-style: italic;
}

@media (max-width: 768px) {
  .admin-container {
    padding: 1rem;
  }
  
  .grid-container {
    grid-template-columns: 1fr;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .upload-section {
    flex-direction: column;
  }
  
  .attachment-info {
    flex-direction: column;
    align-items: start;
    gap: 0.5rem;
  }
  
  .attachment-meta {
    align-items: start;
  }
}
</style>