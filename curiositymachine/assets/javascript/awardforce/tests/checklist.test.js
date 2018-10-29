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
          items: {
            enough_challenges_completed: false,
            email_unique: false,
            email_verified: false,
            post_survey_taken: false,
            family_confirmed_all_listed: false
          } 
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
          items: {
            enough_challenges_completed: true,
            email_unique: true,
            email_verified: true,
            post_survey_taken: true,
            family_confirmed_all_listed: true
          }
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
          complete: true,
          items: {}
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    expect(wrapper.find('.v-create').exists()).toBeTruthy();
    expect(wrapper.find('.v-create').classes()).not.toContain('disabled');
  });

  it('disables button when not complete', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          complete: false,
          items: {}
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    expect(wrapper.find('.v-create').exists()).toBeTruthy();
    expect(wrapper.find('.v-create').classes()).toContain('disabled');
  });

  it('shows family member confirmation controls', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          items: {
            family_confirmed_all_listed: false
          } 
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    expect(wrapper.find('.v-family-controls').exists()).toBeTruthy();
  });

  it('hides family member confirmation controls when previously confirmed', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn().mockImplementation(() => Promise.resolve({
          items: {
            family_confirmed_all_listed: true
          } 
        }))
      }
    });
    const wrapper = mount(Checklist, {});
    await flushPromises();
    expect(wrapper.find('.v-family-controls').exists()).toBeFalsy();
  });

  it('updates when family members confirmed confirmed', async () => {
    Api.mockImplementation(() => {
      return {
        get: jest.fn()
        .mockImplementationOnce(() => Promise.resolve({
          items: {
            family_confirmed_all_listed: false
          } 
        }))
        .mockImplementationOnce(() => Promise.resolve({
          items: {
            family_confirmed_all_listed: true
          } 
        })),
        confirm_family: jest.fn().mockImplementation(() => Promise.resolve())
      }
    });

    const wrapper = mount(Checklist, {});
    await flushPromises();

    expect(wrapper.find('.v-family-controls').exists()).toBeTruthy();

    const btn = wrapper.find('.v-confirm-family');
    btn.trigger("click");
    await flushPromises();

    expect(wrapper.find('.v-family-controls').exists()).toBeFalsy();
    expect(wrapper.find('.v-family-checkbox').classes()).toContain('checkbox-checked');
  });
});
