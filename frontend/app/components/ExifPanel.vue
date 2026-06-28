<template>
  <Transition name="panel-slide">
    <div v-if="visible" class="exif-panel-overlay" @click.self="$emit('close')">
      <div class="exif-panel">
        <div class="panel-header">
          <h3>Image Info</h3>
          <button class="panel-close" @click="$emit('close')">&times;</button>
        </div>
        <div class="panel-body">
          <div v-if="loading" class="panel-loading">Loading...</div>
          <template v-else-if="exif?.hasExif">
            <div class="exif-section">
              <h4 class="section-title">Camera</h4>
              <div class="exif-row"><span class="exif-label">Make</span><span class="exif-value">{{ exif.make || '--' }}</span></div>
              <div class="exif-row"><span class="exif-label">Model</span><span class="exif-value">{{ exif.model || '--' }}</span></div>
            </div>
            <div class="exif-section">
              <h4 class="section-title">Settings</h4>
              <div class="exif-row"><span class="exif-label">Aperture</span><span class="exif-value">{{ formatAperture(exif.aperture) }}</span></div>
              <div class="exif-row"><span class="exif-label">Shutter</span><span class="exif-value">{{ formatShutter(exif.shutterSpeed) }}</span></div>
              <div class="exif-row"><span class="exif-label">ISO</span><span class="exif-value">{{ exif.iso || '--' }}</span></div>
              <div class="exif-row"><span class="exif-label">Focal Length</span><span class="exif-value">{{ formatFocal(exif.focalLength) }}</span></div>
            </div>
            <div class="exif-section">
              <h4 class="section-title">File</h4>
              <div class="exif-row"><span class="exif-label">Date Taken</span><span class="exif-value">{{ exif.dateTaken || '--' }}</span></div>
              <div class="exif-row"><span class="exif-label">Dimensions</span><span class="exif-value">{{ dimensions }}</span></div>
            </div>
          </template>
          <div v-else class="panel-empty">No EXIF data available</div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const props = defineProps({
  visible: { type: Boolean, default: false },
  imageId: { type: Number, default: null },
  dimensions: { type: String, default: '' },
})

const emit = defineEmits(['close'])

const config = useRuntimeConfig()
const exif = ref(null)
const loading = ref(false)

watch(() => props.imageId, (id) => {
  if (id && props.visible) fetchExif(id)
})

watch(() => props.visible, (v) => {
  if (v && props.imageId) fetchExif(props.imageId)
})

async function fetchExif(id) {
  loading.value = true
  exif.value = null
  try {
    const res = await fetch(`${config.public.apiBaseUrl}/api/images/${id}/exif`)
    exif.value = await res.json()
  } catch {
    exif.value = { hasExif: false }
  } finally {
    loading.value = false
  }
}

function formatAperture(v) {
  if (v == null) return '--'
  return `f/${v}`
}

function formatShutter(v) {
  if (v == null) return '--'
  if (v < 1) return `1/${Math.round(1 / v)}`
  return `${v}s`
}

function formatFocal(v) {
  if (v == null) return '--'
  return `${v}mm`
}
</script>

<style scoped>
.exif-panel-overlay {
  position: fixed;
  inset: 0;
  z-index: 1001;
  display: flex;
  justify-content: flex-end;
}

.exif-panel {
  width: 320px;
  max-width: 85vw;
  height: 100%;
  background: rgba(20, 20, 30, 0.95);
  backdrop-filter: blur(16px);
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.4);
  overflow-y: auto;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-header h3 {
  color: #e5e7eb;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.panel-close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.panel-close:hover { color: #e5e7eb; }

.panel-body {
  padding: 0.75rem 1.25rem;
  flex: 1;
}

.panel-loading, .panel-empty {
  color: #9ca3af;
  text-align: center;
  padding: 2rem 0;
  font-size: 0.875rem;
}

.exif-section {
  margin-bottom: 1rem;
}

.section-title {
  color: #a5b4fc;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.5rem 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.exif-row {
  display: flex;
  justify-content: space-between;
  padding: 0.3125rem 0;
  font-size: 0.8125rem;
}

.exif-label {
  color: #9ca3af;
}

.exif-value {
  color: #e5e7eb;
  font-weight: 500;
  text-align: right;
}

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: opacity 0.2s ease;
}

.panel-slide-enter-active .exif-panel,
.panel-slide-leave-active .exif-panel {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
}

.panel-slide-enter-from .exif-panel,
.panel-slide-leave-to .exif-panel {
  transform: translateX(100%);
}
</style>
