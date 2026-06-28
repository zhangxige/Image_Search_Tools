import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'
import { mockUseRuntimeConfig, mockFetch, createMockLog } from '../../__tests__/utils'
import LogsPage from '../logs.vue'

describe('Logs page', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
  })

  it('loads logs on mount', async () => {
    const logs = [
      createMockLog({ id: 1, filename: 'test.jpg', operation: 'ingest' }),
      createMockLog({ id: 2, filename: 'photo.png' }),
    ]
    mockFetch(logs)

    const wrapper = mount(LogsPage)
    await flushPromises()

    expect(wrapper.text()).toContain('test.jpg')
    expect(wrapper.text()).toContain('photo.png')
  })

  it('shows empty state when no logs', async () => {
    mockFetch([])

    const wrapper = mount(LogsPage)
    await flushPromises()

    expect(wrapper.text()).toContain('No logs yet')
  })

  it('shows Load More button when more logs available', async () => {
    const logs = Array.from({ length: 50 }, (_, i) => createMockLog({ id: i + 1 }))
    mockFetch(logs)

    const wrapper = mount(LogsPage)
    await flushPromises()

    expect(wrapper.find('button').text()).toContain('Load More')
  })
})
