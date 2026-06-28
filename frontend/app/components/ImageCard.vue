<template>
  <div class="card image-card" @click="$emit('click')">
    <div class="image-wrapper">
      <img :src="imageUrl" :alt="image.original_filename" loading="lazy" @error="onError" />
      <span v-if="distance !== undefined" class="distance-badge">{{ (distance * 100).toFixed(1) }}%</span>
    </div>
    <div class="image-info">
      <p class="image-name" :title="image.original_filename">{{ image.original_filename }}</p>
      <p class="image-meta">{{ image.width }}x{{ image.height }} &middot; {{ formatSize(image.file_size) }}</p>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

const props = defineProps({
  image: { type: Object, required: true },
  distance: { type: Number, default: undefined },
})

defineEmits(['click'])

const imageUrl = computed(() => {
  return getImageSrc(props.image, config.public.apiBaseUrl)
})

function formatSize(bytes) {
  if (!bytes) return 'Unknown'
  const mb = bytes / (1024 * 1024)
  if (mb >= 1) return `${mb.toFixed(1)} MB`
  return `${(bytes / 1024).toFixed(0)} KB`
}

function onError(e) {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect fill="%23f1f5f9" width="200" height="200"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2394a3b8" font-size="14">No Image</text></svg>'
}
</script>

<style scoped>
.image-card {
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.image-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.image-wrapper {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--bg-surface);
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

.distance-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(99, 102, 241, 0.9);
  color: #fff;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
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
</style>
