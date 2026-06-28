<template>
  <div>
    <h1 class="page-title"><span>&#128214;</span> Ingestion Logs</h1>

    <div v-if="loading" class="spinner" />

    <div v-else-if="logs.length === 0" class="empty-state">
      <div class="icon">&#128203;</div>
      <h3>No logs yet</h3>
      <p>Ingestion logs will appear here after uploading images.</p>
    </div>

    <div v-else class="card" style="overflow: hidden;">
      <div style="overflow-x: auto;">
        <table class="log-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Time</th>
              <th>Operation</th>
              <th>Status</th>
              <th>Filename</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="cell-narrow">{{ log.id }}</td>
              <td class="cell-narrow">{{ formatDate(log.created_at) }}</td>
              <td>{{ log.operation }}</td>
              <td>
                <span class="badge" :class="log.status === 'success' ? 'badge-success' : 'badge-danger'">
                  {{ log.status }}
                </span>
              </td>
              <td class="cell-file">{{ log.filename || '-' }}</td>
              <td class="text-muted" style="font-size: 0.8125rem;">{{ log.message || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="hasMore" style="text-align: center; margin-top: 1.5rem;">
      <button class="btn btn-secondary" :disabled="loadingMore" @click="loadMore">
        {{ loadingMore ? 'Loading...' : 'Load More' }}
      </button>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

const logs = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const skip = ref(0)
const pageSize = 50
const hasMore = ref(true)

async function fetchLogs() {
  try {
    const res = await fetch(`${config.public.apiBaseUrl}/api/images/logs?skip=${skip.value}&limit=${pageSize}`)
    const data = await res.json()
    logs.value.push(...data)
    hasMore.value = data.length === pageSize
  } catch (e) {
    console.error('Failed to fetch logs:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleString()
}

async function loadMore() {
  loadingMore.value = true
  skip.value += pageSize
  await fetchLogs()
}

onMounted(fetchLogs)
</script>

<style scoped>
.log-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.log-table thead {
  background: var(--bg-surface);
}

.log-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.log-table td {
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--border-light);
  color: var(--text);
}

.log-table tbody tr:hover {
  background: var(--bg-surface);
}

.cell-narrow {
  white-space: nowrap;
}

.cell-file {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
