import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppFooter from '../AppFooter.vue'

describe('AppFooter', () => {
  it('renders current year', () => {
    const wrapper = mount(AppFooter)
    const year = new Date().getFullYear()
    expect(wrapper.text()).toContain(String(year))
  })

  it('renders project attribution', () => {
    const wrapper = mount(AppFooter)
    expect(wrapper.text()).toContain('Powered by Xception + FAISS')
  })
})
