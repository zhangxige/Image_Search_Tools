<template>
  <div>
    <h1 class="page-title"><span>&#128269;</span> Image Search</h1>

    <!-- Upload query -->
    <div class="card" style="padding: 1.5rem; margin-bottom: 1.5rem;">
      <div
        class="file-drop"
        :class="{ dragover: dragging }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
      >
        <div class="icon">&#128269;</div>
        <p style="font-weight: 600; margin-bottom: 0.25rem;">
          Drop query image(s) here
        </p>
        <p class="text-muted">
          Upload 1 or more images to find similar results
        </p>
        <input ref="fileInput" type="file" multiple accept="image/*,.heic,.heif,.heics,.avif" @change="onFileSelect" />
      </div>

      <div v-if="queryFiles.length > 0" class="file-list">
        <div v-for="(f, i) in queryFiles" :key="i" class="file-tag">
          <span>{{ f.name }}</span>
          <button @click="removeFile(i)">&times;</button>
        </div>
      </div>

      <div class="form-group" style="margin-top: 1rem;">
        <label for="topK">Top-K results</label>
        <input id="topK" v-model.number="topK" type="number" min="1" max="50" style="width: 100px;" />
      </div>

      <div style="margin-top: 1rem;">
        <button
          class="btn btn-primary"
          :disabled="queryFiles.length === 0 || searching"
          @click="searchImages"
        >
          {{ searching ? 'Searching...' : 'Search' }}
        </button>
      </div>

      <!-- Query preview -->
      <div v-if="queryPreviews.length > 0" style="margin-top: 1rem;">
        <p class="text-muted" style="font-weight: 600; margin-bottom: 0.5rem;">Query Images:</p>
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
          <div
            v-for="(src, i) in queryPreviews"
            :key="i"
            class="query-thumb"
            @click="openQueryPreview(i)"
          >
            <img :src="src" />
            <span class="query-label">{{ queryFiles[i]?.name }}</span>
          </div>
        </div>
      </div>

      <div v-if="searching" class="spinner" style="margin-top: 1.5rem;" />
    </div>

    <!-- Results -->
    <div v-if="results">
      <div v-if="results.length === 0" class="empty-state">
        <div class="icon">&#128270;</div>
        <h3>No results found</h3>
        <p>Try uploading different images.</p>
      </div>

      <div v-else>
        <h2 style="margin-bottom: 1rem; font-size: 1.125rem; font-weight: 600;">
          Results <span class="text-muted" style="font-weight: 400;">({{ results.length }})</span>
        </h2>

        <div class="results-list">
          <div
            v-for="r in results"
            :key="r.image.id"
            class="card result-row"
          >
            <div class="result-images">
              <div class="result-group">
                <p class="result-label">Query</p>
                <div class="result-img-wrapper" @click="openQueryPreview(0)">
                  <img :src="queryPreviews[0]" class="result-img" />
                  <div class="zoom-hint">&#128269;</div>
                </div>
                <p class="result-filename">{{ queryFiles[0]?.name }}</p>
              </div>

              <div class="vs-col">
                <div class="vs-badge">{{ (r.distance * 100).toFixed(1) }}%</div>
                <div class="vs-bar">
                  <div class="vs-fill" :style="{ width: (r.distance * 100) + '%' }" />
                </div>
              </div>

              <div class="result-group">
                <p class="result-label">Match</p>
                <div class="result-img-wrapper" @click="openResultPreview(r.image)">
                  <img
                    :src="getImageSrc(r.image, config.public.apiBaseUrl)"
                    class="result-img"
                  />
                  <div class="zoom-hint">&#128269;</div>
                </div>
                <p class="result-filename">{{ r.image.original_filename }}</p>
                <div v-if="r.image.tags" style="margin-top: 0.25rem; display: flex; gap: 0.25rem; justify-content: center; flex-wrap: wrap;">
                  <span v-for="tag in (r.image.tags || '').split(',').map(t => t.trim()).filter(Boolean).slice(0, 3)" :key="tag" class="search-tag">{{ tag }}</span>
                </div>
                <button
                  class="btn btn-export"
                  :disabled="exportingIndex === results.indexOf(r)"
                  @click="exportToDir(r, results.indexOf(r))"
                >
                  {{ exportingIndex === results.indexOf(r) ? 'Exporting...' : '&#128229; Export' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Export toast -->
        <Transition name="toast">
          <div v-if="exportMessage" class="toast" :class="exportType" @click="exportMessage = ''">
            {{ exportMessage }}
          </div>
        </Transition>
      </div>
    </div>

    <ImagePreview :image="previewImage" :visible="previewVisible" @close="previewVisible = false" />
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

const dragging = ref(false)
const queryFiles = ref([])
const queryPreviews = ref([])
const searching = ref(false)
const results = ref(null)
const topK = ref(5)
const fileInput = ref(null)

const previewImage = ref(null)
const previewVisible = ref(false)

const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'heic', 'heif', 'avif']

function isImageFile(f) {
  if (f.type.startsWith('image/')) return true
  const ext = f.name.split('.').pop()?.toLowerCase()
  return IMAGE_EXTS.includes(ext)
}

const exportingIndex = ref(-1)
const exportMessage = ref('')
const exportType = ref('success')
let exportTimer = null

function onDrop(e) {
  dragging.value = false
  addFiles([...e.dataTransfer.files].filter(isImageFile))
}

function onFileSelect(e) {
  addFiles([...e.target.files].filter(isImageFile))
  e.target.value = ''
}

const HEIC_EXTS = ['heic', 'heif', 'heics', 'avif']

async function getHeicPreviewUrl(file) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await fetch(`${config.public.apiBaseUrl}/api/images/preview`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) throw new Error(res.statusText)
    const blob = await res.blob()
    return URL.createObjectURL(blob)
  } catch {
    return null
  }
}

function addFiles(files) {
  for (const f of files) {
    if (queryPreviews.value.length >= 5) break
    const idx = queryFiles.value.length
    queryFiles.value.push(f)
    const ext = f.name.split('.').pop()?.toLowerCase()
    if (HEIC_EXTS.includes(ext)) {
      queryPreviews.value.push(null)
      getHeicPreviewUrl(f).then(url => {
        if (idx < queryPreviews.value.length && queryFiles.value[idx] === f) {
          queryPreviews.value[idx] = url || null
        }
      })
    } else {
      const reader = new FileReader()
      reader.onload = (e) => queryPreviews.value.push(e.target.result)
      reader.readAsDataURL(f)
    }
  }
}

function removeFile(i) {
  const removed = queryPreviews.value[i]
  queryFiles.value.splice(i, 1)
  queryPreviews.value.splice(i, 1)
  if (removed && removed.startsWith('blob:')) URL.revokeObjectURL(removed)
}

function openQueryPreview(i) {
  previewImage.value = { filename: queryPreviews.value[i], original_filename: queryFiles.value[i]?.name }
  previewVisible.value = true
}

function openResultPreview(img) {
  previewImage.value = img
  previewVisible.value = true
}

function showExportMessage(msg, type = 'success') {
  exportMessage.value = msg
  exportType.value = type
  clearTimeout(exportTimer)
  exportTimer = setTimeout(() => { exportMessage.value = '' }, 4000)
}

async function exportToDir(result, idx) {
  exportingIndex.value = idx
  try {
    if (!window.showDirectoryPicker) {
      showExportMessage('Your browser does not support directory export. Try Chrome or Edge.', 'error')
      exportingIndex.value = -1
      return
    }

    const dirHandle = await window.showDirectoryPicker()

    // 1. Write label file
    const labelContent = JSON.stringify({
      query_file: queryFiles.value[0]?.name || 'unknown',
      top1_match: {
        id: result.image.id,
        filename: result.image.original_filename,
        stored_as: result.image.filename,
        similarity_pct: (result.distance * 100).toFixed(1),
        tags: result.image.tags || '',
      },
      exported_at: new Date().toISOString(),
    }, null, 2)

    const labelFile = await dirHandle.getFileHandle('top1_match.json', { create: true })
    const labelWriter = await labelFile.createWritable()
    await labelWriter.write(labelContent)
    await labelWriter.close()

    // 2. Write query image
    const queryFile = queryFiles.value[0]
    if (queryFile) {
      const imgHandle = await dirHandle.getFileHandle(queryFile.name, { create: true })
      const imgWriter = await imgHandle.createWritable()
      await imgWriter.write(await queryFile.slice().arrayBuffer())
      await imgWriter.close()
    }

    showExportMessage(`Exported to ${dirHandle.name}`, 'success')
  } catch (e) {
    if (e.name === 'AbortError' || e.name === 'SecurityError') {
      showExportMessage('Export cancelled', 'error')
    } else {
      console.error('Export failed:', e)
      showExportMessage(`Export failed: ${e.message}`, 'error')
    }
  } finally {
    exportingIndex.value = -1
  }
}

onUnmounted(() => clearTimeout(exportTimer))

async function searchImages() {
  if (queryFiles.value.length === 0) return
  searching.value = true
  results.value = null

  const formData = new FormData()
  for (const file of queryFiles.value) {
    formData.append('files', file)
  }
  formData.append('top_k', topK.value.toString())

  try {
    const res = await fetch(`${config.public.apiBaseUrl}/api/search`, {
      method: 'POST',
      body: formData,
    })
    const data = await res.json()
    results.value = data.results
  } catch (e) {
    console.error('Search failed:', e)
  } finally {
    searching.value = false
  }
}
</script>

<style scoped>
.query-thumb {
  position: relative;
  width: 130px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 2px solid var(--border);
  cursor: pointer;
  transition: border-color 0.2s;
  background: var(--bg-card);
}

.query-thumb:hover {
  border-color: var(--primary);
}

.query-thumb img {
  width: 100%;
  height: 100px;
  object-fit: cover;
  display: block;
}

.query-label {
  display: block;
  padding: 0.25rem 0.5rem;
  font-size: 0.6875rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-row {
  padding: 1.25rem;
}

.result-images {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.result-group {
  flex: 1;
  min-width: 180px;
  text-align: center;
}

.result-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.result-img-wrapper {
  position: relative;
  aspect-ratio: 1;
  max-width: 200px;
  margin: 0 auto;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  cursor: pointer;
}

.result-img-wrapper:hover .zoom-hint {
  opacity: 1;
}

.result-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.zoom-hint {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
}

.result-filename {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-tag {
  display: inline-block;
  padding: 0.0625rem 0.375rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 500;
  line-height: 1.4;
}

.vs-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 60px;
}

.vs-badge {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--primary);
  white-space: nowrap;
}

.vs-bar {
  width: 60px;
  height: 4px;
  background: var(--bg-surface);
  border-radius: 2px;
  overflow: hidden;
}

.vs-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.btn-export {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--bg-surface);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
}

.btn-export:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text);
  border-color: var(--text-muted);
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 9999;
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
}

.toast.success {
  background: var(--success-light);
  color: var(--success);
  border-color: var(--success);
}

.toast.error {
  background: var(--danger-light);
  color: var(--danger);
  border-color: var(--danger);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(1rem);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}
</style>
