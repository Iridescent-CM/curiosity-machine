import { mount, shallowMount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import SingleComment from '../SingleComment.vue'
import Api from '../api'

jest.mock('../api');

describe('single-comment', () => {
  it('is disabled with disabled api', () => {
    Api.mockImplementation(() => {
      return {
        disabled: true
      };
    });
    var wrapper = mount(SingleComment);
    expect(wrapper.find('textarea').is(':disabled')).toBeTruthy();
    expect(wrapper.findAll('button').is(':disabled')).toBeTruthy();
  });

  it('shows controls without comment', () => {
    var wrapper = mount(SingleComment);
    expect(wrapper.find('textarea').isVisible()).toBeTruthy();
  });

  it('shows comment', async () => {
    Api.mockImplementation(() => {
      return {
        disabled: false,
        list: jest.fn(function() {
          return Promise.resolve([
            {id: 2}
          ]);
        })
      };
    });
    var wrapper = shallowMount(SingleComment, {
      propsData: {
        author: "5",
        progress: "6"
      }
    });
    await flushPromises();
    expect(wrapper.find('textarea').exists()).not.toBeTruthy();
    expect(wrapper.find('comment-stub').exists()).toBeTruthy();
  });

  it('checks for comment by role', () => {
    Api.mockImplementation(() => {
      return {
        disabled: false,
        list: jest.fn(function() {
          return Promise.resolve([
            {id: 2}
          ]);
        })
      };
    });
    var wrapper = shallowMount(SingleComment, {
      propsData: {
        author: "5",
        progress: "6",
        role: "somerole",
      }
    });
    expect(wrapper.vm.$data.api.list).toBeCalledWith("somerole");
  });

  it('creates new comment', async () => {
    Api.mockImplementation(() => {
      return {
        disabled: false,
        list: jest.fn(function() {
          return Promise.resolve([]);
        }),
        create: jest.fn(function() {
          return Promise.resolve({id: 10});
        })
      };
    });
    var wrapper = mount(SingleComment, {
      propsData: {
        author: "5",
        progress: "6",
        role: "somerole",
      }
    });

    var textarea = wrapper.find('textarea');
    textarea.element.value = 'a new comment';
    textarea.trigger('input');
    wrapper.find('button[type="submit"]').trigger('click');

    await flushPromises();

    expect(wrapper.vm.$data.api.create).toBeCalledWith({
      role: "somerole",
      text: "a new comment"
    });
  });

  it('removes comment', async () => {
    Api.mockImplementation(() => {
      return {
        disabled: false,
        list: jest.fn(function() {
          return Promise.resolve([
            {id: 2}
          ]);
        })
      };
    });
    var wrapper = shallowMount(SingleComment, {
      propsData: {
        author: "5",
        progress: "6",
        role: "somerole",
      }
    });

    await flushPromises();

    expect(wrapper.find('comment-stub').exists()).toBeTruthy();
    wrapper.vm.remove();
    expect(wrapper.find('comment-stub').exists()).not.toBeTruthy();
  });
});
