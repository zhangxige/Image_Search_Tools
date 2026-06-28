<template>
  <div class="hdr-badge" :class="[sizeClass]" :title="tooltipText">
    <svg class="hdr-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 8v8" />
      <path d="M3 12h4" />
      <path d="M7 8v8" />
      <path d="M12 8h2.5a2.5 2.5 0 0 1 0 5H12" />
      <path d="M12 13h1.5a2.5 2.5 0 0 1 0 5H12" />
      <path d="M19.5 8H17v8h2.5" />
      <path d="M17 12h2" />
    </svg>
    <span v-if="size === 'large'" class="hdr-text">HDR</span>
  </div>
</template>

<script setup>
const props = defineProps({
  format: { type: String, default: '' },
  size: { type: String, default: 'small', validator: v => ['small', 'large'].includes(v) },
})

const sizeClass = computed(() => `hdr-badge--${props.size}`)

const tooltipText = computed(() => {
  if (props.format) return `HDR: ${props.format}`
  return 'HDR'
})
</script>

<style scoped>
.hdr-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  background: rgba(251, 191, 36, 0.2);
  border: 1px solid rgba(251, 191, 36, 0.5);
  border-radius: 4px;
  color: #fbbf24;
  cursor: default;
  position: relative;
}

.hdr-badge:hover::after {
  content: attr(title);
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: #e2e8f0;
  padding: 0.375rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.hdr-badge:hover::before {
  content: '';
  position: absolute;
  bottom: calc(100% + 2px);
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #1e293b;
  z-index: 10;
  pointer-events: none;
}

.hdr-badge--small {
  width: 22px;
  height: 22px;
  padding: 2px;
}

.hdr-badge--small .hdr-icon {
  width: 14px;
  height: 14px;
}

.hdr-badge--large {
  padding: 0.25rem 0.5rem;
  gap: 0.375rem;
}

.hdr-badge--large .hdr-icon {
  width: 18px;
  height: 18px;
}

.hdr-text {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}
</style>
