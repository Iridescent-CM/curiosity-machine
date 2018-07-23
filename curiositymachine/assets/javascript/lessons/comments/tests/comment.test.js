import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import Comment from '../Comment.vue'
import Api from '../api'

jest.mock('../filestack_wrapper');
jest.mock('../api');

global.confirm = jest.fn();
global.confirm.mockReturnValue(true);


describe('Comment', () => {

  it('shows text comment', () => {
    const wrapper = mount(Comment, {
      propsData: {
        initial: {
          text: "a text comment"
        }
      }
    });
    expect(wrapper.html()).toEqual(expect.stringContaining("a text comment"));
  });

  it('shows image uploads', () => {
    const wrapper = mount(Comment, {
      propsData: {
        initial: {
          upload: {
            type: "image",
            url: "http://example.com/url"
          }
        } 
      }
    });
    const img = wrapper.find('img');
    expect(img.exists()).toBeTruthy();
    expect(img.attributes().src).toBe('http://example.com/url');
  });

  it('shows encoded videos', () => {
    const wrapper = mount(Comment, {
      propsData: {
        initial: {
          upload: {
            type: "video",
            url: "http://example.com/url",
            encodings: [
              {
                "url": "http://example.com/encoding1",
                "mimetype": "video/mp4"
              },
              {
                "url": "http://example.com/encoding2",
                "mimetype": "video/ogg"
              }
            ],
            thumbnail: ""
          }
        }
      }
    });
    const vid = wrapper.find('video');
    expect(vid.exists()).toBeTruthy();
    expect(vid.findAll('source')).toHaveLength(2);

  });

  it('shows not-yet-encoded videos', () => {
    const wrapper = mount(Comment, {
      propsData: {
        initial: {
          upload: {
            type: "video",
            url: "http://example.com/url",
            encodings: [],
            thumbnail: ""
          }
        }
      }
    });
    const vid = wrapper.find('video');
    expect(vid.exists()).toBeTruthy();
    expect(vid.attributes().src).toBe('http://example.com/url');
  });

});

describe("Comment removal", () => {
  let wrapper;
  let api;

  beforeEach(() => {
    api = {
      disabled: false,
      list: function () {
        return Promise.resolve([]);
      },
      destroy: jest.fn(function () {
        return Promise.resolve({});  
      })
    };

    wrapper = mount(Comment, {
      propsData: {
        initial: {
          id: 5,
          text: "a text comment"
        },
        api: api
      }
    });
  });

  it('calls API', () => {
    const btn = wrapper.find('button');
    expect(btn.text()).toEqual("Remove");
    btn.trigger("click");
    expect(api.destroy).toBeCalledWith(5);
  });

  it('emits event', async () => {
    const btn = wrapper.find('button');
    expect(btn.text()).toEqual("Remove");
    btn.trigger("click");
    await flushPromises();
    expect(wrapper.emitted().remove).toBeTruthy();
  });
});

// shows error when error?
// reverts text on edit cancel
