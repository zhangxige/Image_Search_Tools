import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mockUseRuntimeConfig, mockFetch, mockFetchSequence, createMockImage } from '../../__tests__/utils'
import SearchPage from '../search.vue'

describe('Search page', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
    mockFetch(['xception', 'resnet50', 'clip'])
  })

  const stubs = {
    ImagePreview: { template: '<div />' },
  }

  it('disables search button when no images', async () => {
    const wrapper = mount(SearchPage, { global: { stubs } })
    await flushPromises()

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
    await flushPromises()

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

  it('fetches available models on mount and populates dropdown', async () => {
    const wrapper = mount(SearchPage, { global: { stubs } })
    await flushPromises()

    const select = wrapper.find('#modelSelect')
    expect(select.exists()).toBe(true)
    expect(wrapper.vm.availableModels).toEqual(['xception', 'resnet50', 'clip'])
    expect(wrapper.vm.selectedModel).toBe('xception')
  })

  it('sends selected model in search request', async () => {
    mockFetch({ results: [] })

    const wrapper = mount(SearchPage, { global: { stubs } })
    await flushPromises()

    await wrapper.setData({
      selectedModel: 'clip',
      queryFiles: [new File(['data'], 'q.jpg', { type: 'image/jpeg' })],
      queryPreviews: ['data:image/png;base64,fake'],
    })

    const searchBtn = wrapper.find('.btn-primary')
    await searchBtn.trigger('click')
    await flushPromises()

    const fetchCalls = vi.mocked(fetch).mock.calls
    const searchCall = fetchCalls.find(c => c[0].includes('/api/search'))
    expect(searchCall).toBeDefined()
    expect(searchCall[0]).toContain('model=clip')
  })

  it('displays model badge after search', async () => {
    mockFetch({
      results: [
        { image: createMockImage({ id: 1 }), distance: 0.85 },
      ],
    })

    const wrapper = mount(SearchPage, { global: { stubs } })
    await flushPromises()

    await wrapper.setData({
      selectedModel: 'resnet50',
      queryFiles: [new File(['data'], 'q.jpg', { type: 'image/jpeg' })],
      queryPreviews: ['data:image/png;base64,fake'],
    })

    const searchBtn = wrapper.find('.btn-primary')
    await searchBtn.trigger('click')
    await flushPromises()

    expect(wrapper.find('.model-badge').exists()).toBe(true)
    expect(wrapper.find('.model-badge').text()).toBe('resnet50')
  })
})
