import pytest
from profiles.factories import *
from ..factories import *
from ..serializers import *

def test_quiz_serialization():
    quiz = QuizFactory.build()
    data = QuizSerializer(quiz).data
    assert data == {
        "answered": False,
        "questions": [
            {
                "answered": False,
                "text": quiz.question_1,
                "options": [
                    {
                        "text": quiz.answer_1_1,
                        "selected": False
                    },
                    {
                        "text": quiz.answer_1_2,
                        "selected": False
                    },
                    {
                        "text": quiz.answer_1_3,
                        "selected": False
                    }
                ]
            }
        ],
        "answers": []
    }

@pytest.mark.django_db
def test_correct_quiz_and_result_serialization():
    taker = UserFactory()
    quiz = QuizFactory()
    result = QuizResultFactory(quiz=quiz, answer_1=1, taker=taker)
    data = QuizAndResultSerializer(result).data
    assert data == {
        "answered": True,
        "correct": True,
        "questions": [
            {
                "answered": True,
                "correct": True,
                "text": quiz.question_1,
                "options": [
                    {
                        "text": quiz.answer_1_1,
                        "selected": True
                    },
                    {
                        "text": quiz.answer_1_2,
                        "selected": False
                    },
                    {
                        "text": quiz.answer_1_3,
                        "selected": False
                    }
                ]
            }
        ],
        "answers": [1]
    }

@pytest.mark.django_db
def test_incorrect_quiz_and_result_serialization():
    taker = UserFactory()
    quiz = QuizFactory()
    result = QuizResultFactory(quiz=quiz, answer_1=2, taker=taker)
    data = QuizAndResultSerializer(result).data
    assert data == {
        "answered": True,
        "correct": False,
        "questions": [
            {
                "answered": True,
                "correct": False,
                "text": quiz.question_1,
                "options": [
                    {
                        "text": quiz.answer_1_1,
                        "selected": False
                    },
                    {
                        "text": quiz.answer_1_2,
                        "selected": True
                    },
                    {
                        "text": quiz.answer_1_3,
                        "selected": False
                    }
                ]
            }
        ],
        "answers": [2]
    }

@pytest.mark.django_db
def test_quiz_result_serialization():
    taker = UserFactory()
    quiz = QuizFactory()
    result = QuizResultFactory(quiz=quiz, answer_1=1, taker=taker)
    data = QuizResultSerializer(result).data
    assert data == {
        'quiz': quiz.id,
        'taker': taker.id,
        'answers': [result.answer_1]
    }

@pytest.mark.django_db
def test_quiz_result_deserialization():
    taker = UserFactory()
    quiz = QuizFactory()
    serializer = QuizResultSerializer(data={
        'quiz': quiz.id,
        'taker': taker.id,
        'answers': [3]
    })
    assert serializer.is_valid()
    obj = serializer.save()
    assert obj.answer_1 == 3
