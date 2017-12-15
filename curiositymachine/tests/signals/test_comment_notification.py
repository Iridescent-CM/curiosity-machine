import pytest
from challenges.factories import *
from cmcomments.factories import *
from mentors.factories import *
from students.factories import *
from ...signals.handlers import recipients_for

def test_student_without_mentor():
    student = StudentFactory.build()
    progress = ProgressFactory.build(student=student)
    comment = CommentFactory.build(user=student, challenge_progress=progress)

    assert recipients_for(comment, student) == []

def test_student_with_mentor():
    student = StudentFactory.build()
    mentor = MentorFactory.build()
    progress = ProgressFactory.build(student=student, mentor=mentor)
    comment = CommentFactory.build(user=student, challenge_progress=progress)

    assert recipients_for(comment, student) == [mentor]

def test_mentor():
    student = StudentFactory.build()
    mentor = MentorFactory.build()
    progress = ProgressFactory.build(student=student, mentor=mentor)
    comment = CommentFactory.build(user=student, challenge_progress=progress)

    assert recipients_for(comment, mentor) == [student]

def test_other():
    student = StudentFactory.build()
    mentor = MentorFactory.build()
    other = MentorFactory.build()
    progress = ProgressFactory.build(student=student, mentor=mentor)
    comment = CommentFactory.build(user=student, challenge_progress=progress)

    assert recipients_for(comment, other) == [student]
