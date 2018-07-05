import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import Comments from '../Comments.vue'
import Api from '../api'

jest.mock('../filestack_wrapper');
jest.mock('../api');

describe('with api disabled', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation(() => {
      return {
        disabled: true,
        list: jest.fn()
      };
    });
  });

  beforeEach(async () => {
    wrapper = mount(Comments);
    await flushPromises();
  });

  it('disables the controls', () => {
    expect(wrapper.findAll('textarea').is(':disabled')).toBeTruthy();
    expect(wrapper.findAll('button').is(':disabled')).toBeTruthy();
  });

  it('gets no comments', () => {
    const data = wrapper.vm.$data;
    expect(data.comments).toHaveLength(0);
    expect(data.api.list).not.toBeCalled();
  });
});

describe('with api enabled', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation((opts) => {
      return {
        _opts: opts,
        disabled: false,
        list: jest.fn(function() {
          return Promise.resolve([]);  
        })
      };
    });
  });

  beforeEach(async () => {
    wrapper = mount(Comments);
    await flushPromises();
  });

  it('initializes Api from props', () => {
    wrapper = mount(Comments, {
      propsData: {
        author: 5,
        progress: 6
      }
    });
    expect(wrapper.vm.$data.api._opts).toEqual({
      author: 5,
      progress: 6
    });
  });

  it('enables the controls', () => {
    expect(wrapper.findAll('textarea').is(':disabled')).toBeFalsy();
    expect(wrapper.findAll('button').is(':disabled')).toBeFalsy();
  });

  it('gets comments from Api', () => {
    const data = wrapper.vm.$data;
    expect(data.api.list).toBeCalled();
  });
});

describe('with comments', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation(() => {
      return {
        disabled: false,
        list: function () {
          return Promise.resolve([]);
        }
      };
    });
  });

  beforeEach(() => {
    wrapper = mount(Comments);
  });

  it('shows text comments', () => {
    wrapper.setData({
      comments: [{text: "a text comment"}]
    });
    expect(wrapper.html()).toEqual(expect.stringContaining("a text comment"));
  });

  it('shows image uploads', () => {
    wrapper.setData({
      comments: [{
        upload: {
          type: "image",
          url: "http://example.com/url"
        }
      }]
    });
    const img = wrapper.find('img');
    expect(img.exists()).toBeTruthy();
    expect(img.attributes().src).toBe('http://example.com/url');
  });

  it('shows encoded videos', () => {
    wrapper.setData({
      comments: [{
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
      }]
    });
    const vid = wrapper.find('video');
    expect(vid.exists()).toBeTruthy();
    expect(vid.findAll('source')).toHaveLength(2);

  });

  it('shows not-yet-encoded videos', () => {
    wrapper.setData({
      comments: [{
        upload: {
          type: "video",
          url: "http://example.com/url",
          encodings: [],
          thumbnail: ""
        }
      }]
    });
    const vid = wrapper.find('video');
    expect(vid.exists()).toBeTruthy();
    expect(vid.attributes().src).toBe('http://example.com/url');
  });

});

// shows error when error?
// reverts text on edit cancel
