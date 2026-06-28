import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mockUseRuntimeConfig, mockFetch, createMockImage } from '../../__tests__/utils'
import UploadPage from '../upload.vue'

function createMockFile(name = 'test.jpg') {
  return new File(['fake-image-content'], name, { type: 'image/jpeg' })
}

describe('Upload page', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
  })

  const stubs = {
    ImageCard: { props: ['image'], template: '<div class="mock-image">{{ image.original_filename }}</div>' },
  }

  it('submits files with tags', async () => {
    const result = { success: [createMockImage()], failed: [] }
    mockFetch(result)

    const wrapper = mount(UploadPage, { global: { stubs } })
    const file = createMockFile()

    await wrapper.setData({ files: [file], tags: 'nature,landscape' })

    const uploadBtn = wrapper.find('.btn-primary')
    await uploadBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('uploaded successfully')
    expect(wrapper.text()).toContain('test.jpg')
  })

  it('shows upload button disabled when no files', () => {
    const wrapper = mount(UploadPage, { global: { stubs } })

    const uploadBtn = wrapper.find('.btn-primary')
    expect(uploadBtn.attributes('disabled')).toBeDefined()
  })
})
