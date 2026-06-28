import { vi } from 'vitest'

export function mockUseRuntimeConfig(overrides = {}) {
  const config = {
    public: {
      apiBaseUrl: 'http://localhost:8000',
      githubRepo: '',
      ...overrides,
    },
  }
  vi.stubGlobal('useRuntimeConfig', vi.fn(() => config))
}

export function createMockImage(overrides = {}) {
  return {
    id: 1,
    original_filename: 'test.jpg',
    filename: 'abc123.jpg',
    width: 800,
    height: 600,
    file_size: 102400,
    tags: 'nature,landscape',
    ...overrides,
  }
}

export function createMockLog(overrides = {}) {
  return {
    id: 1,
    created_at: '2026-06-16T12:00:00Z',
    operation: 'ingest',
    status: 'success',
    filename: 'test.jpg',
    message: 'Ingested successfully',
    ...overrides,
  }
}

export function mockFetch(jsonResponse, status = 200) {
  const response = new Response(JSON.stringify(jsonResponse), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(response)))
}

export function mockFetchSequence(...responses) {
  const fns = responses.map(([data, status = 200]) => {
    return () => Promise.resolve(
      new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' },
      })
    )
  })
  const mock = vi.fn()
  fns.forEach((fn) => mock.mockImplementationOnce(fn))
  vi.stubGlobal('fetch', mock)
}

export const NuxtLinkStub = {
  props: ['to'],
  template: '<a :href="to"><slot /></a>',
}
