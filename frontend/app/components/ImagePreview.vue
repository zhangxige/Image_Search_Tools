<template>
  <Teleport to="body">
    <Transition name="preview-fade">
      <div v-if="visible" class="overlay" @click.self="close" @keydown="onKeydown">
        <div class="frosted-bg" :style="frostedBgStyle" />
        <div class="preview-content">
          <div class="top-bar">
            <div class="top-left">
              <span class="file-name">{{ image?.original_filename || 'Preview' }}</span>
              <HdrBadge v-if="image?.is_hdr" :format="image?.hdr_format" size="large" />
              <span v-if="isRemote" class="file-dims">{{ image?.width }}x{{ image?.height }} &middot; {{ formatSize(image?.file_size) }}</span>
            </div>
            <div class="top-right">
              <button class="icon-btn" @click="showExif = !showExif" title="Image info">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              </button>
              <button class="icon-btn" @click="close" title="Close">&times;</button>
            </div>
          </div>

          <div class="image-area">
            <button class="nav-btn nav-prev" @click="prev" :disabled="!hasPrev">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div class="image-wrapper">
              <img :key="displaySrc" :src="displaySrc" :alt="image?.original_filename || 'preview'" class="preview-img" @error="onError" />
            </div>
            <button class="nav-btn nav-next" @click="next" :disabled="!hasNext">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>

          <!-- Tags bar -->
          <div class="bottom-bar">
            <div v-if="isRemote" class="tags-section">
              <div class="tags-row">
                <span v-for="(tag, i) in tagList" :key="i" class="tag-pill">{{ tag }}</span>
                <button v-if="!editingTags" class="btn-ghost btn-tag-edit" @click="startEdit" title="Edit tags">&#9998;</button>
              </div>
              <div v-if="editingTags" class="tag-edit-row">
                <input ref="tagInput" v-model="editValue" type="text" placeholder="comma-separated tags" class="tag-input" @keydown.enter="saveTags" @keydown.escape="cancelEdit" />
                <button class="btn btn-primary btn-tag-save" @click="saveTags">Save</button>
                <button class="btn btn-secondary" @click="cancelEdit">Cancel</button>
              </div>
            </div>
          </div>
        </div>

        <ExifPanel
          :visible="showExif"
          :image-id="image?.id"
          :dimensions="image ? `${image.width}x${image.height}` : ''"
          @close="showExif = false"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const config = useRuntimeConfig()

const props = defineProps({
  image: { type: Object, default: null },
  visible: { type: Boolean, default: false },
  images: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'prev', 'next', 'tags-updated'])

const editingTags = ref(false)
const editValue = ref('')
const saving = ref(false)
const tagInput = ref(null)
const showExif = ref(false)

const isRemote = computed(() => props.image?.filename && !props.image.filename.startsWith('data:'))

const displaySrc = computed(() => {
  return getImageSrc(props.image, config.public.apiBaseUrl)
})

const frostedBgStyle = computed(() => {
  if (!displaySrc.value) return {}
  return {
    backgroundImage: `url(${displaySrc.value})`,
    backgroundSize: '120%',
    backgroundPosition: 'center',
    filter: 'blur(40px) brightness(0.6)',
    transform: 'scale(1.1)',
  }
})

const currentIndex = computed(() => {
  if (!props.image?.id || !props.images.length) return -1
  return props.images.findIndex(img => img.id === props.image.id)
})

const hasPrev = computed(() => currentIndex.value > 0)
const hasNext = computed(() => currentIndex.value >= 0 && currentIndex.value < props.images.length - 1)

const tagList = computed(() => {
  const raw = props.image?.tags || ''
  return raw.split(',').map(t => t.trim()).filter(Boolean)
})

watch(() => props.visible, (v) => {
  if (v) showExif.value = false
})

function formatSize(bytes) {
  if (!bytes) return ''
  const mb = bytes / (1024 * 1024)
  if (mb >= 1) return `${mb.toFixed(1)} MB`
  return `${(bytes / 1024).toFixed(0)} KB`
}

function onError(e) {
  if (isRemote.value) {
    e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect fill="%23334155" width="200" height="200"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2394a3b8" font-size="14">Load Failed</text></svg>'
  }
}

function close() { editingTags.value = false; emit('close') }
function prev() { editingTags.value = false; if (hasPrev.value) emit('prev', currentIndex.value - 1) }
function next() { editingTags.value = false; if (hasNext.value) emit('next', currentIndex.value + 1) }

function startEdit() {
  editValue.value = props.image?.tags || ''
  editingTags.value = true
  nextTick(() => tagInput.value?.focus())
}

function cancelEdit() {
  editingTags.value = false
  editValue.value = ''
}

async function saveTags() {
  if (!props.image?.id) return
  saving.value = true
  try {
    const res = await fetch(`${config.public.apiBaseUrl}/api/images/${props.image.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tags: editValue.value }),
    })
    const updated = await res.json()
    emit('tags-updated', updated)
    editingTags.value = false
  } catch (e) {
    console.error('Failed to save tags:', e)
  } finally {
    saving.value = false
  }
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    if (showExif.value) showExif.value = false
    else if (editingTags.value) cancelEdit()
    else close()
  }
  if (!editingTags.value && !showExif.value) {
    if (e.key === 'ArrowLeft') prev()
    if (e.key === 'ArrowRight') next()
  }
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
}

.frosted-bg {
  position: absolute;
  inset: -20px;
  z-index: -1;
}

.preview-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 0.75rem;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  flex-shrink: 0;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-name {
  color: #e5e7eb;
  font-weight: 600;
  font-size: 0.875rem;
}

.file-dims {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8125rem;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon-btn {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: #e5e7eb;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.375rem;
  transition: background 0.2s;
}

.icon-btn:hover { background: rgba(255, 255, 255, 0.18); }

.image-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-height: 0;
}

.image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 90%;
  max-height: 85vh;
}

.preview-img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 8px 48px rgba(0, 0, 0, 0.6);
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.06);
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  z-index: 5;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s, color 0.2s;
  margin: 0 0.5rem;
}

.nav-btn:hover:not(:disabled) { background: rgba(255, 255, 255, 0.15); color: #fff; }
.nav-btn:disabled { opacity: 0.15; cursor: default; }
.nav-prev { left: 0.5rem; }
.nav-next { right: 0.5rem; }

.bottom-bar {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  padding: 0.5rem 0;
}

.tags-section { text-align: center; }

.tags-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.tag-pill {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: rgba(99, 102, 241, 0.25);
  color: #a5b4fc;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.btn-tag-edit {
  color: rgba(255,255,255,0.5) !important;
  font-size: 0.875rem;
  margin-left: 0.25rem;
}

.btn-tag-edit:hover {
  color: #e5e7eb !important;
  background: rgba(255,255,255,0.1) !important;
}

.tag-edit-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag-input {
  padding: 0.375rem 0.625rem;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 6px;
  font-size: 0.8125rem;
  background: rgba(255,255,255,0.08);
  color: #e5e7eb;
  width: 220px;
  outline: none;
}

.tag-input:focus { border-color: var(--primary); }

.btn-tag-save { padding: 0.375rem 0.75rem; font-size: 0.75rem; }

.preview-fade-enter-active,
.preview-fade-leave-active {
  transition: opacity 0.2s ease;
}
.preview-fade-enter-from,
.preview-fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .preview-content { padding: 0.25rem; }
  .nav-btn { width: 2.25rem; height: 2.25rem; }
  .nav-btn svg { width: 18px; height: 18px; }
  .file-name { font-size: 0.75rem; }
  .file-dims { font-size: 0.6875rem; }
}
</style>
