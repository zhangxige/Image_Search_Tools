<template>
  <div>
    <div class="flex-between">
      <h1 class="page-title">
        <span>&#128247;</span> Gallery
        <span v-if="totalCount !== null" class="text-muted" style="font-weight: 400;">
          {{ totalCount }} image{{ totalCount !== 1 ? 's' : '' }}
        </span>
      </h1>
      <div class="flex-center">
        <button
          v-if="selectedIds.size > 0"
          class="btn btn-danger"
          @click="showDeleteConfirm = true"
        >
          Delete {{ selectedIds.size }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="spinner" />

    <div v-else-if="images.length === 0" class="empty-state">
      <div class="icon">&#128247;</div>
      <h3 v-if="tagFilter">No images match "{{ tagFilter }}"</h3>
      <h3 v-else>No images yet</h3>
      <p v-if="tagFilter" style="margin-bottom: 1rem;">Try a different tag or clear the filter.</p>
      <p v-else style="margin-bottom: 1rem;">Upload some images to get started.</p>
      <button v-if="tagFilter" class="btn btn-secondary" @click="clearTagFilter">Clear Filter</button>
      <NuxtLink v-else to="/upload" class="btn btn-primary">Upload Images</NuxtLink>
    </div>

    <template v-else>
      <!-- Toolbar -->
      <div class="toolbar">
        <label class="checkbox-wrapper">
          <input
            type="checkbox"
            :checked="allSelected"
            :indeterminate.prop="someSelected && !allSelected"
            @change="toggleSelectAll"
          />
          <span class="checkbox-visual" />
          <span class="toolbar-label">{{ selectedIds.size > 0 ? `${selectedIds.size} selected` : 'Select All' }}</span>
        </label>
        <span class="toolbar-divider" />
        <div class="tag-filter">
          <input
            v-model="tagFilter"
            type="text"
            placeholder="Filter by tag... (Enter to search)"
            class="tag-filter-input"
            @keydown.enter="applyTagFilter"
          />
          <button class="btn btn-primary btn-filter-apply" :disabled="!tagFilter" @click="applyTagFilter">Search</button>
          <button v-if="tagFilter" class="btn-ghost btn-clear-filter" @click="clearTagFilter">&times;</button>
        </div>
      </div>

      <!-- Grid -->
      <div class="grid">
        <div
          v-for="img in images"
          :key="img.id"
          class="card image-card"
          :class="{ selected: selectedIds.has(img.id) }"
        >
          <div class="image-wrapper" @dblclick="openPreview(img)">
            <img
              :src="getImageUrl(img)"
              :alt="img.original_filename"
              loading="lazy"
              @error="onImgError"
              @click="openPreview(img)"
            />
            <label class="select-overlay" @click.stop @change="toggleSelect(img.id)">
              <input type="checkbox" :checked="selectedIds.has(img.id)" />
              <span class="check-visual" />
            </label>
            <HdrBadge v-if="img.is_hdr" :format="img.hdr_format" size="small" class="hdr-badge-card" />
          </div>
          <div class="image-info">
            <p class="image-name" :title="img.original_filename">{{ img.original_filename }}</p>
            <p class="image-meta">{{ img.width }}x{{ img.height }} &middot; {{ formatSize(img.file_size) }}</p>
            <div class="card-tags">
              <template v-if="img.tags">
                <span v-for="tag in parseTags(img.tags).slice(0, 2)" :key="tag" class="card-tag">{{ tag }}</span>
                <span v-if="parseTags(img.tags).length > 2" class="card-tag-more">+{{ parseTags(img.tags).length - 2 }}</span>
              </template>
              <span v-else class="card-tag card-tag-empty">No Tag</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="btn btn-secondary" :disabled="page <= 1" @click="goPage(page - 1)">
          &laquo;
        </button>
        <button
          v-for="p in visiblePages"
          :key="p"
          class="btn"
          :class="p === page ? 'btn-primary' : 'btn-secondary'"
          @click="goPage(p)"
        >
          {{ p }}
        </button>
        <button class="btn btn-secondary" :disabled="page >= totalPages" @click="goPage(page + 1)">
          &raquo;
        </button>
      </div>
    </template>

    <!-- Preview modal with keyboard nav -->
    <ImagePreview
      :image="previewImage"
      :visible="previewVisible"
      :images="images"
      @close="previewVisible = false"
      @prev="goPreviewImage"
      @next="goPreviewImage"
      @tags-updated="onTagsUpdated"
    />

    <!-- Delete confirmation -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="overlay" @click.self="showDeleteConfirm = false">
        <div class="modal">
          <h3>Delete {{ selectedIds.size }} image{{ selectedIds.size > 1 ? 's' : '' }}?</h3>
          <p class="text-muted" style="margin-top: 0.25rem;">This action cannot be undone.</p>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteConfirm = false">Cancel</button>
            <button class="btn btn-danger" :disabled="deleting" @click="deleteSelected">
              {{ deleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

const images = ref([])
const loading = ref(true)
const totalCount = ref(null)
const page = ref(1)
const pageSize = 30
const tagFilter = ref('')

const previewImage = ref(null)
const previewVisible = ref(false)

const selectedIds = ref(new Set())
const showDeleteConfirm = ref(false)
const deleting = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil((totalCount.value || 0) / pageSize)))

const visiblePages = computed(() => {
  const pages = []
  const tp = totalPages.value
  const cp = page.value
  let start = Math.max(1, cp - 2)
  let end = Math.min(tp, cp + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(tp, start + 4)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const allSelected = computed(() => images.value.length > 0 && images.value.every(img => selectedIds.value.has(img.id)))

const someSelected = computed(() => selectedIds.value.size > 0)

function getImageUrl(img) {
  return getImageSrc(img, config.public.apiBaseUrl)
}

function formatSize(bytes) {
  if (!bytes) return 'Unknown'
  const mb = bytes / (1024 * 1024)
  if (mb >= 1) return `${mb.toFixed(1)} MB`
  return `${(bytes / 1024).toFixed(0)} KB`
}

function onImgError(e) {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect fill="%23f1f5f9" width="200" height="200"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2394a3b8" font-size="14">No Image</text></svg>'
}

function openPreview(img) {
  previewImage.value = img
  previewVisible.value = true
}

function goPreviewImage(index) {
  if (index >= 0 && index < images.value.length) {
    previewImage.value = images.value[index]
  }
}

function parseTags(raw) {
  return (raw || '').split(',').map(t => t.trim()).filter(Boolean)
}

function onTagsUpdated(updated) {
  const idx = images.value.findIndex(img => img.id === updated.id)
  if (idx !== -1) {
    images.value[idx] = updated
    previewImage.value = updated
  }
}

function toggleSelect(id) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  selectedIds.value = s
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(images.value.map(img => img.id))
  }
}

async function deleteSelected() {
  deleting.value = true
  const ids = [...selectedIds.value]
  try {
    await fetch(`${config.public.apiBaseUrl}/api/images?image_ids=${ids.join('&image_ids=')}`, {
      method: 'DELETE',
    })
    selectedIds.value = new Set()
    showDeleteConfirm.value = false
    await fetchImages()
  } catch (e) {
    console.error('Delete failed:', e)
  } finally {
    deleting.value = false
  }
}

async function fetchImages() {
  const skip = (page.value - 1) * pageSize
  const tagParam = tagFilter.value ? `&tag=${encodeURIComponent(tagFilter.value)}` : ''
  try {
    const [imagesRes, countRes] = await Promise.all([
      fetch(`${config.public.apiBaseUrl}/api/images?skip=${skip}&limit=${pageSize}${tagParam}`),
      fetch(`${config.public.apiBaseUrl}/api/images/count?${tagParam ? tagParam.slice(1) : ''}`),
    ])
    images.value = await imagesRes.json()
    totalCount.value = (await countRes.json()).count
    // Remove any selected IDs that no longer exist
    const existing = new Set(images.value.map(img => img.id))
    selectedIds.value = new Set([...selectedIds.value].filter(id => existing.has(id)))
  } catch (e) {
    console.error('Failed to fetch images:', e)
  } finally {
    loading.value = false
  }
}

function applyTagFilter() {
  page.value = 1
  selectedIds.value = new Set()
  loading.value = true
  fetchImages()
}

function clearTagFilter() {
  tagFilter.value = ''
  page.value = 1
  selectedIds.value = new Set()
  loading.value = true
  fetchImages()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  selectedIds.value = new Set()
  loading.value = true
  fetchImages()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(fetchImages)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.625rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: background var(--transition), border-color var(--transition);
}

.toolbar-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.toolbar-divider {
  width: 1px;
  height: 1.25rem;
  background: var(--border);
}

.image-card {
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}

.image-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.image-card.selected {
  outline: 3px solid var(--primary);
  outline-offset: -3px;
}

.image-wrapper {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--bg-surface);
  cursor: pointer;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.image-wrapper:hover img {
  transform: scale(1.05);
}

.select-overlay {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-card:hover .select-overlay,
.image-card.selected .select-overlay {
  opacity: 1;
}

.select-overlay input {
  display: none;
}

.check-visual {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.3);
  transition: all 0.2s;
  position: relative;
}

.select-overlay input:checked + .check-visual {
  background: var(--primary);
  border-color: var(--primary);
}

.select-overlay input:checked + .check-visual::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 6px;
  height: 10px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.image-info {
  padding: 0.625rem 0.75rem;
}

.image-name {
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
}

.image-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.125rem;
}

.card-tags {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.375rem;
  flex-wrap: wrap;
}

.card-tag {
  display: inline-block;
  padding: 0.0625rem 0.375rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 500;
  line-height: 1.4;
}

.card-tag-more {
  font-size: 0.6875rem;
  color: var(--text-muted);
  line-height: 1.6;
}

.card-tag-empty {
  background: var(--bg-surface);
  color: var(--text-muted);
  font-style: italic;
}

.hdr-badge-card {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 2;
}

.tag-filter {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: auto;
}

.tag-filter-input {
  padding: 0.375rem 0.625rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  background: var(--bg-card);
  color: var(--text);
  width: 180px;
  outline: none;
  transition: border-color var(--transition);
}

.tag-filter-input:focus {
  border-color: var(--primary);
}

.tag-filter-input::placeholder {
  color: var(--text-muted);
}

.btn-clear-filter {
  font-size: 1.125rem;
  line-height: 1;
  padding: 0.125rem 0.375rem;
}

.btn-filter-apply {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  flex-shrink: 0;
}
</style>
