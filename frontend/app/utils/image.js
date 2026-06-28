const BROWSER_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']

export function getImageSrc(image, apiBaseUrl) {
  if (!image) return ''
  const filename = image.filename || image
  if (!filename) return ''
  if (filename.startsWith('data:')) return filename
  const ext = '.' + filename.split('.').pop().toLowerCase()
  if (BROWSER_FORMATS.includes(ext)) {
    return `${apiBaseUrl}/uploads/${filename}`
  }
  const id = image.id
  if (id == null) return ''
  return `${apiBaseUrl}/api/images/${id}/file`
}
