import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { mockUseRuntimeConfig, createMockImage } from '../../__tests__/utils'
import ImageCard from '../ImageCard.vue'

describe('ImageCard', () => {
  beforeEach(() => {
    mockUseRuntimeConfig()
  })

  it('displays filename and metadata', () => {
    const image = createMockImage()
    const wrapper = mount(ImageCard, {
      props: { image },
    })

    expect(wrapper.text()).toContain('test.jpg')
    expect(wrapper.text()).toContain('800x600')
    expect(wrapper.text()).toContain('100 KB')
  })

  it('emits click event', () => {
    const image = createMockImage()
    const wrapper = mount(ImageCard, {
      props: { image },
    })

    wrapper.trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('shows distance badge when distance prop provided', () => {
    const image = createMockImage()
    const wrapper = mount(ImageCard, {
      props: { image, distance: 0.85 },
    })

    expect(wrapper.text()).toContain('85.0%')
  })
})
