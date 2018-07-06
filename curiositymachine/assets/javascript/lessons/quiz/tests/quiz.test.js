import { mount } from '@vue/test-utils'
import Quiz from '../Quiz.vue'
import Api from '../api'

jest.mock('../api');

describe('with no taker', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation(() => {
      return {
        get_quiz: jest.fn(function() {

          return Promise.resolve({
            answered: false,
            questions: [
              {
                answered: false,
                text: "q1 text",
                options: [
                  { text: "q1 o1 text", selected: false },
                  { text: "q1 o2 text", selected: false },
                  { text: "q1 o3 text", selected: false }
                ]
              }
            ],
            answers: []
          });

        })
      };
    });
  });

  beforeEach(async () => {
    wrapper = mount(Quiz, {
      propsData: {
        quizId: 1
      }
    });
  });

  it('shows the quiz', () => {
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o2 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o3 text"));
  });

  it('disables radio buttons', () => {
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3);
    expect(wrapper.findAll('input[type="radio"]').is(':disabled')).toBeTruthy();
  });

  it('disables the submit button', () => {
    expect(wrapper.findAll('button')).toHaveLength(1);
    expect(wrapper.findAll('button').is(':disabled')).toBeTruthy();
  });
});

describe('quiz not yet taken', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation(() => {
      return {
        get_quiz: jest.fn(function() {

          return Promise.resolve({
            answered: false,
            questions: [
              {
                answered: false,
                text: "q1 text",
                options: [
                  { text: "q1 o1 text", selected: false },
                  { text: "q1 o2 text", selected: false },
                  { text: "q1 o3 text", selected: false }
                ]
              }
            ],
            answers: []
          });

        })
      };
    });
  });

  beforeEach(async () => {
    wrapper = mount(Quiz, {
      propsData: {
        quizId: 1,
        takerId: 1
      }
    });
  });

  it('shows the quiz', () => {
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o2 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o3 text"));
  });

  it('has radio buttons enabled', () => {
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3);
    expect(wrapper.findAll('input[type="radio"]').is(':enabled')).toBeTruthy();
  });

  it('enables submit button after selection', () => {
    expect(wrapper.findAll('button')).toHaveLength(1);
    expect(wrapper.find('button').is(':disabled')).toBeTruthy();

    wrapper.findAll('input[type="radio"]').at(1).setChecked();

    expect(wrapper.find('button').is(':enabled')).toBeTruthy();
  });
});

describe('quiz with wrong answer', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation(() => {
      return {
        get_quiz: jest.fn(function() {

          return Promise.resolve({
            answered: true,
            correct: false,
            questions: [
              {
                answered: true,
                correct: false,
                text: "q1 text",
                options: [
                  { text: "q1 o1 text", selected: true },
                  { text: "q1 o2 text", selected: false },
                  { text: "q1 o3 text", selected: false }
                ]
              }
            ],
            answers: [1]
          });

        })
      };
    });
  });

  beforeEach(async () => {
    wrapper = mount(Quiz, {
      propsData: {
        quizId: 1,
        takerId: 1
      }
    });
  });

  it('shows the quiz', () => {
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o2 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o3 text"));
  });

  it('has radio buttons enabled', () => {
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3);
    expect(wrapper.findAll('input[type="radio"]').is(':enabled')).toBeTruthy();
  });

  it('shows the selected answer with an X', () => {
    var container = wrapper.findAll('.form-check').at(0);
    var radio = container.find('input[type="radio"]');
    expect(radio.is(':checked')).toBeTruthy();
    expect(container.find('.grading-mark-incorrect').exists()).toBeTruthy();
  });

  it('has submit button enabled', () => {
    expect(wrapper.findAll('button')).toHaveLength(1);
    expect(wrapper.findAll('button').is(':enabled')).toBeTruthy();
  });
});

describe('quiz with correct answer', () => {
  let wrapper;

  beforeAll(() => {
    Api.mockImplementation(() => {
      return {
        get_quiz: jest.fn(function() {

          return Promise.resolve({
            answered: true,
            correct: true,
            questions: [
              {
                answered: true,
                correct: true,
                text: "q1 text",
                options: [
                  { text: "q1 o1 text", selected: true },
                  { text: "q1 o2 text", selected: false },
                  { text: "q1 o3 text", selected: false }
                ]
              }
            ],
            answers: [1]
          });

        })
      };
    });
  });

  beforeEach(async () => {
    wrapper = mount(Quiz, {
      propsData: {
        quizId: 1,
        takerId: 1
      }
    });
  });

  it('shows the quiz', () => {
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o1 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o2 text"));
    expect(wrapper.html()).toEqual(expect.stringContaining("q1 o3 text"));
  });

  it('marks quiz as correct', () => {
    expect(wrapper.find('.quiz.correct').exists()).toBeTruthy();
  });

  it('has radio buttons disabled', () => {
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3);
    expect(wrapper.findAll('input[type="radio"]').is(':disabled')).toBeTruthy();
  });

  it('shows the selected answer with a checkmark', () => {
    var container = wrapper.findAll('.form-check').at(0);
    var radio = container.find('input[type="radio"]');
    expect(radio.is(':checked')).toBeTruthy();
    expect(container.find('.grading-mark-correct').exists()).toBeTruthy();
  });

  it('hides submit button', () => {
    expect(wrapper.findAll('button')).toHaveLength(0);
  });
});
