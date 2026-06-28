import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mockUseRuntimeConfig, mockFetchSequence, createMockImage, NuxtLinkStub } from '../../__tests__/utils'
import GalleryPage from '../index.vue'

describe('Gallery page', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
  })

  const stubs = {
    NuxtLink: NuxtLinkStub,
    ImagePreview: { template: '<div />' },
  }

  it('loads images on mount', async () => {
    const images = [createMockImage({ id: 1 }), createMockImage({ id: 2, original_filename: 'photo.png' })]
    mockFetchSequence(
      [images],
      [{ count: 2 }],
    )

    const wrapper = mount(GalleryPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).toContain('test.jpg')
    expect(wrapper.text()).toContain('photo.png')
  })

  it('shows empty state when no images', async () => {
    mockFetchSequence(
      [[]],
      [{ count: 0 }],
    )

    const wrapper = mount(GalleryPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).toContain('No images yet')
    expect(wrapper.text()).not.toContain('test.jpg')
  })

  it('shows pagination when more than 30 images', async () => {
    const images = Array.from({ length: 30 }, (_, i) => createMockImage({ id: i + 1 }))
    mockFetchSequence(
      [images],
      [{ count: 45 }],
    )

    const wrapper = mount(GalleryPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.find('.pagination').exists()).toBe(true)
  })

  it('select-all checkbox toggles all', async () => {
    const images = [createMockImage({ id: 1 }), createMockImage({ id: 2 })]
    mockFetchSequence(
      [images],
      [{ count: 2 }],
    )

    const wrapper = mount(GalleryPage, { global: { stubs } })
    await flushPromises()

    const selectAllCheckbox = wrapper.find('.toolbar input[type="checkbox"]')
    await selectAllCheckbox.setValue(true)
    expect(wrapper.text()).toContain('Delete 2')

    await selectAllCheckbox.setValue(false)
    expect(wrapper.text()).not.toContain('Delete')
  })
})
