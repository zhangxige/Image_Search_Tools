import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, h } from 'vue'
import { mockUseRuntimeConfig } from '../../__tests__/utils'
import NavBar from '../NavBar.vue'

const NuxtLinkStub = {
  props: ['to'],
  template: '<a :href="to"><slot /></a>',
}

function mockUseTheme() {
  const isDark = ref(false)
  vi.stubGlobal('useTheme', vi.fn(() => ({
    isDark,
    toggle: () => { isDark.value = !isDark.value },
  })))
}

describe('NavBar', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
    mockUseTheme()
  })

  it('renders all nav links', () => {
    const wrapper = mount(NavBar, {
      global: {
        stubs: { NuxtLink: NuxtLinkStub },
      },
    })

    expect(wrapper.text()).toContain('Gallery')
    expect(wrapper.text()).toContain('Upload')
    expect(wrapper.text()).toContain('Search')
    expect(wrapper.text()).toContain('Logs')
  })

  it('renders GitHub link from runtime config', () => {
    mockUseRuntimeConfig({ githubRepo: 'owner/repo' })
    const wrapper = mount(NavBar, {
      global: {
        stubs: { NuxtLink: NuxtLinkStub },
      },
    })

    const githubLink = wrapper.find('.github-star')
    expect(githubLink.attributes('href')).toBe('https://github.com/owner/repo')
  })

  it('renders default GitHub link when no repo configured', () => {
    mockUseRuntimeConfig({ githubRepo: '' })
    const wrapper = mount(NavBar, {
      global: {
        stubs: { NuxtLink: NuxtLinkStub },
      },
    })

    const githubLink = wrapper.find('.github-star')
    expect(githubLink.attributes('href')).toBe('https://github.com')
  })

  it('renders theme toggle button', () => {
    const wrapper = mount(NavBar, {
      global: {
        stubs: { NuxtLink: NuxtLinkStub },
      },
    })

    const toggleBtn = wrapper.find('.theme-toggle')
    expect(toggleBtn.exists()).toBe(true)
  })

  it('toggles theme on button click', async () => {
    const wrapper = mount(NavBar, {
      global: {
        stubs: { NuxtLink: NuxtLinkStub },
      },
    })

    const toggleBtn = wrapper.find('.theme-toggle')
    // Initially isDark=false -> shows moon icon
    expect(toggleBtn.html()).toContain('\u{1F319}')
    await toggleBtn.trigger('click')
    // After toggle isDark=true -> shows sun icon
    expect(toggleBtn.html()).toContain('\u{1F31E}')
  })
})
