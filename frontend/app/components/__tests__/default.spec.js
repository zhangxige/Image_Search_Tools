import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { mockUseRuntimeConfig } from '../../__tests__/utils'
import defaultLayout from '../../layouts/default.vue'

describe('default layout', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
  })

  it('renders NavBar', () => {
    const wrapper = mount(defaultLayout, {
      global: {
        stubs: { NavBar: true, AppFooter: true },
      },
      slots: {
        default: '<div class="slot-content">Content</div>',
      },
    })

    expect(wrapper.findComponent({ name: 'NavBar' }).exists()).toBe(true)
  })

  it('renders AppFooter', () => {
    const wrapper = mount(defaultLayout, {
      global: {
        stubs: { NavBar: true, AppFooter: true },
      },
      slots: {
        default: '<div class="slot-content">Content</div>',
      },
    })

    expect(wrapper.findComponent({ name: 'AppFooter' }).exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(defaultLayout, {
      global: {
        stubs: { NavBar: true, AppFooter: true },
      },
      slots: {
        default: '<div class="slot-content">Content</div>',
      },
    })

    expect(wrapper.find('.slot-content').exists()).toBe(true)
    expect(wrapper.find('.slot-content').text()).toBe('Content')
  })
})
