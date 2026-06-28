import { describe, it, expect, beforeEach, vi } from 'vitest'
import { defineComponent, createApp } from 'vue'
import { useTheme } from '../useTheme'

const STORAGE_KEY = 'theme-preference'

function mockMatchMedia(prefersDark = false) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)' ? prefersDark : false,
      media: query,
    })),
  })
}

function mountComposable() {
  let result
  const app = createApp(defineComponent({
    setup() {
      result = useTheme()
      return () => null
    },
  }))
  const el = document.createElement('div')
  app.mount(el)
  app.unmount()
  return result
}

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    mockMatchMedia(false)
  })

  it('toggles from light to dark', () => {
    const { isDark, toggle } = mountComposable()

    expect(isDark.value).toBe(false)
    toggle()
    expect(isDark.value).toBe(true)
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('toggles from dark to light', () => {
    const { isDark, toggle } = mountComposable()

    toggle()
    expect(isDark.value).toBe(true)

    toggle()
    expect(isDark.value).toBe(false)
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })

  it('persists preference in localStorage', () => {
    const { toggle } = mountComposable()

    toggle()
    expect(localStorage.getItem(STORAGE_KEY)).toBe('dark')

    toggle()
    expect(localStorage.getItem(STORAGE_KEY)).toBe('light')
  })

  it('restores preference from localStorage', () => {
    localStorage.setItem(STORAGE_KEY, 'dark')

    const { isDark } = mountComposable()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('falls back to prefers-color-scheme when no stored preference', () => {
    mockMatchMedia(true)

    const { isDark } = mountComposable()

    expect(isDark.value).toBe(true)
  })

  it('falls back to light when no stored preference and system prefers light', () => {
    mockMatchMedia(false)

    const { isDark } = mountComposable()

    expect(isDark.value).toBe(false)
  })

  it('sets data-theme attribute on html element', () => {
    const { toggle } = mountComposable()

    toggle()
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')

    toggle()
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })
})
