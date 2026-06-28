<template>
  <div>
    <NavBar />
    <main class="page container">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import NavBar from '~/components/NavBar.vue'
import AppFooter from '~/components/AppFooter.vue'
</script>
