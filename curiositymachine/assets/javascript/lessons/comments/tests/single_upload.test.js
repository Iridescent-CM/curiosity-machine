import { mount, shallowMount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import SingleUpload from '../SingleUpload.vue'
import Api from '../api'
import init from '../filestack_wrapper'

jest.mock('../filestack_wrapper');
jest.mock('../api');

describe('single-upload', () => {
  it('is disabled with disabled api', () => {
    Api.mockImplementation(() => {
      return {
        disabled: true
      };
    });
    var wrapper = mount(SingleUpload);
    expect(wrapper.findAll('button').is(':disabled')).toBeTruthy();
  });

  it('shows controls without comment', () => {
    var wrapper = mount(SingleUpload);
    var btn = wrapper.find('button');
    expect(btn.text()).toEqual(expect.stringContaining("Choose"));
    expect(btn.isVisible()).toBeTruthy();
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
    var wrapper = shallowMount(SingleUpload, {
      propsData: {
        author: "5",
        progress: "6"
      }
    });
    await flushPromises();
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
    var wrapper = shallowMount(SingleUpload, {
      propsData: {
        author: "5",
        progress: "6",
        role: "somerole",
      }
    });
    expect(wrapper.vm.$data.api.list).toBeCalledWith("somerole");
  });

  it('creates new comment', async () => {
    init.mockImplementation(() => {
      return {
        pick: jest.fn(() => {
          return Promise.resolve({"upload": "data"});
        })
      }
    });
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
    var wrapper = mount(SingleUpload, {
      propsData: {
        author: "5",
        progress: "6",
        role: "somerole",
      }
    });
    await flushPromises();

    wrapper.find('button').trigger('click');
    await flushPromises();

    expect(wrapper.vm.$data.api.create).toBeCalledWith({
      role: "somerole",
      upload: {"upload": "data"}
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
    var wrapper = shallowMount(SingleUpload, {
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
