import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mockUseRuntimeConfig, mockFetch, createMockImage } from '../../__tests__/utils'
import SearchPage from '../search.vue'

describe('Search page', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
  })

  const stubs = {
    ImagePreview: { template: '<div />' },
  }

  it('disables search button when no images', () => {
    const wrapper = mount(SearchPage, { global: { stubs } })

    const searchBtn = wrapper.find('.btn-primary')
    expect(searchBtn.attributes('disabled')).toBeDefined()
  })

  it('sends search request with top-K and displays results', async () => {
    const result = {
      results: [
        { image: createMockImage({ id: 1, tags: 'cat' }), distance: 0.92 },
        { image: createMockImage({ id: 2, original_filename: 'match.png', tags: '' }), distance: 0.75 },
      ],
    }
    mockFetch(result)

    const wrapper = mount(SearchPage, { global: { stubs } })

    const file = new File(['fake-image'], 'query.jpg', { type: 'image/jpeg' })
    await wrapper.setData({
      queryFiles: [file],
      queryPreviews: ['data:image/png;base64,fake'],
    })

    const searchBtn = wrapper.find('.btn-primary')
    await searchBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('92.0%')
    expect(wrapper.text()).toContain('75.0%')
    expect(wrapper.text()).toContain('cat')
  })
})
