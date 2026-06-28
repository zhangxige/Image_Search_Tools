<template>
  <footer class="footer">
    <div class="container footer-inner">
      <p>&copy; {{ year }} ImageSearch &mdash; Powered by Xception + FAISS</p>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style scoped>
.footer {
  border-top: 1px solid var(--border);
  background: var(--bg-card);
  transition: background var(--transition), border-color var(--transition);
  margin-top: 3rem;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 3rem;
}

.footer p {
  font-size: 0.8125rem;
  color: var(--text-muted);
}
</style>
