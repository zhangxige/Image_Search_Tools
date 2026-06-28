<template>
  <nav class="navbar">
    <div class="container nav-inner">
      <NuxtLink to="/" class="nav-brand">
        <span class="brand-icon">&#128269;</span>
        <span class="brand-text">ImageSearch</span>
      </NuxtLink>

      <div class="nav-links">
        <NuxtLink to="/" class="nav-link" active-class="active">
          <span>&#128247;</span> Gallery
        </NuxtLink>
        <NuxtLink to="/upload" class="nav-link" active-class="active">
          <span>&#128228;</span> Upload
        </NuxtLink>
        <NuxtLink to="/search" class="nav-link" active-class="active">
          <span>&#128269;</span> Search
        </NuxtLink>
        <NuxtLink to="/logs" class="nav-link" active-class="active">
          <span>&#128214;</span> Logs
        </NuxtLink>
      </div>

      <div class="nav-actions">
        <a v-if="githubUrl" :href="githubUrl" target="_blank" rel="noopener" class="github-star" title="GitHub repository">
          <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
          <span>Star</span>
        </a>
        <button class="theme-toggle" @click="toggle" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
          <span v-if="isDark">&#127774;</span>
          <span v-else>&#127769;</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
const { isDark, toggle } = useTheme()
const config = useRuntimeConfig()
const githubUrl = computed(() => {
  const repo = config.public.githubRepo
  if (!repo) return 'https://github.com'
  return `https://github.com/${repo}`
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  border-bottom: 1px solid var(--border);
  z-index: 100;
  transition: background var(--transition), border-color var(--transition);
  backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--bg-card) 85%, transparent);
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text);
  font-weight: 700;
  font-size: 1.125rem;
}

.brand-icon {
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  text-decoration: none;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition);
}

.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text);
}

.nav-link.active {
  background: var(--primary-light);
  color: var(--primary);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.github-star {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: all var(--transition);
  background: var(--bg-surface);
}

.github-star:hover {
  color: var(--text);
  background: var(--bg-hover);
  border-color: var(--text-muted);
}

.theme-toggle {
  width: 2.375rem;
  height: 2.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 1.125rem;
  transition: all var(--transition);
  color: var(--text-secondary);
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text);
}
</style>
