import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import Checklist from '../Checklist.vue'
import Api from '../api'

jest.mock('../api');

describe('Checklist', () => {
  it('shows unchecked', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          challenges_completed: 0,
          enough_challenges_completed: false,
          email_unique: false,
          email_verified: false,
          post_survey_taken: false,
          family_confirmed_all_listed: false
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    wrapper.findAll('.checkbox').wrappers.forEach((wrapper) => {
      expect(wrapper.classes()).not.toContain('checkbox-checked');
    });
  });

  it('shows checked', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          challenges_completed: 0,
          enough_challenges_completed: true,
          email_unique: true,
          email_verified: true,
          post_survey_taken: true,
          family_confirmed_all_listed: true
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    wrapper.findAll('.checkbox').wrappers.forEach((wrapper) => {
      expect(wrapper.classes()).toContain('checkbox-checked');
    });
  });

  it('enables button when complete', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          complete: true
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    expect(wrapper.find('.btn').exists()).toBeTruthy();
    expect(wrapper.find('.btn').classes()).not.toContain('disabled');
  });

  it('hides button when not complete', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          complete: false
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    expect(wrapper.find('.btn').exists()).toBeTruthy();
    expect(wrapper.find('.btn').classes()).toContain('disabled');
  });
});
