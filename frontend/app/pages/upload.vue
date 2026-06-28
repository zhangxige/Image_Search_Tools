<template>
  <div>
    <h1 class="page-title"><span>&#128228;</span> Upload Images</h1>

    <div class="card" style="padding: 1.5rem;">
      <div
        class="file-drop"
        :class="{ dragover: dragging }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
      >
        <div class="icon">&#128206;</div>
        <p style="font-weight: 600; margin-bottom: 0.25rem;">
          Drag & drop images here
        </p>
<p class="text-muted">
  or click to browse &middot; JPG, PNG, WebP, HEIC, AVIF
</p>
        <input ref="fileInput" type="file" multiple accept="image/*,.heic,.heif,.heics,.avif" @change="onFileSelect" />
      </div>

      <div v-if="files.length > 0" class="file-list">
        <div v-for="(f, i) in files" :key="i" class="file-tag">
          <span>{{ f.name }}</span>
          <button @click="removeFile(i)">&times;</button>
        </div>
      </div>

      <div style="margin-top: 1rem;">
        <button
          class="btn btn-primary"
          :disabled="files.length === 0 || uploading"
          @click="uploadFiles"
        >
          {{ uploading ? 'Uploading...' : `Upload ${files.length} Image${files.length !== 1 ? 's' : ''}` }}
        </button>
        <span v-if="uploading" class="spinner" style="width: 24px; height: 24px; margin: 0 0 0 0.75rem; display: inline-block;" />
      </div>
    </div>

      <div class="form-group" style="margin-top: 1rem;">
        <label for="uploadTags">Tags <span class="text-muted" style="font-weight: 400;">(comma-separated, optional)</span></label>
        <input
          id="uploadTags"
          v-model="tags"
          type="text"
          placeholder="e.g. landscape, nature, vacation"
          style="max-width: 400px;"
        />
      </div>

      <div v-if="result" style="margin-top: 1.5rem;">
      <div v-if="result.success.length > 0" class="card" style="padding: 1rem 1.25rem; margin-bottom: 1rem;">
        <h3 style="margin-bottom: 0.75rem; color: var(--success);">
          &#10003; {{ result.success.length }} uploaded successfully
        </h3>
        <div class="grid">
          <ImageCard v-for="img in result.success" :key="img.id" :image="img" />
        </div>
      </div>

      <div v-if="result.failed.length > 0" class="card" style="padding: 1rem 1.25rem;">
        <h3 style="margin-bottom: 0.75rem; color: var(--danger);">
          &#10007; {{ result.failed.length }} failed
        </h3>
        <ul style="list-style: none; font-size: 0.875rem;">
          <li v-for="f in result.failed" :key="f.filename" style="padding: 0.25rem 0; color: var(--text-secondary);">
            <strong>{{ f.filename }}</strong>: {{ f.error }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

const dragging = ref(false)
const files = ref([])
const uploading = ref(false)
const result = ref(null)
const tags = ref('')
const fileInput = ref(null)

const IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.heic', '.heif', '.heics', '.avif']

function isImageFile(f) {
  return f.type.startsWith('image/') || IMAGE_EXTS.includes('.' + (f.name?.split('.').pop() || '').toLowerCase())
}

function onDrop(e) {
  dragging.value = false
  files.value.push(...[...e.dataTransfer.files].filter(isImageFile))
}

function onFileSelect(e) {
  files.value.push(...[...e.target.files].filter(isImageFile))
  e.target.value = ''
}

function removeFile(i) {
  files.value.splice(i, 1)
}

async function uploadFiles() {
  if (files.value.length === 0) return
  uploading.value = true
  result.value = null

  const formData = new FormData()
  for (const file of files.value) {
    formData.append('files', file)
  }
  formData.append('tags', tags.value)

  try {
    const res = await fetch(`${config.public.apiBaseUrl}/api/ingest`, {
      method: 'POST',
      body: formData,
    })
    result.value = await res.json()
    files.value = []
    tags.value = ''
  } catch (e) {
    console.error('Upload failed:', e)
    result.value = { success: [], failed: [{ filename: 'Error', error: e.message }] }
  } finally {
    uploading.value = false
  }
}
</script>
