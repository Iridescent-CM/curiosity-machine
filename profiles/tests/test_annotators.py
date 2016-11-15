import pytest
from mock import Mock

from django.utils.timezone import now
from datetime import timedelta

from cmcomments.factories import *
from profiles.factories import *

from ..annotators import UserCommentSummary

def test_progress_total_with_no_comments():
    summary = UserCommentSummary([], 1).annotate(Mock())
    assert summary.total_user_comments == 0
    assert summary.latest_user_comment == None
    assert summary.user_comment_counts_by_stage == [0, 0, 0, 0]
    assert summary.complete == False

def test_progress_total_with_one_comment():
    user = UserFactory.build()
    comments = [CommentFactory.build(stage=1, user=user)]
    summary = UserCommentSummary(comments, user.id).annotate(Mock())
    assert summary.total_user_comments == 1
    assert summary.latest_user_comment == comments[0]
    assert summary.user_comment_counts_by_stage == [1, 0, 0, 0]
    assert summary.complete == False

def test_progress_total_with_many_comments():
    user = UserFactory.build()
    comments = CommentFactory.build_batch(15, user=user)
    summary = UserCommentSummary(comments, user.id).annotate(Mock())
    assert summary.total_user_comments == 15
    assert sum(summary.user_comment_counts_by_stage) == 15

def test_progress_total_with_reflect_comment_is_complete():
    user = UserFactory.build()
    comments = [CommentFactory.build(stage=4, user=user)]
    summary = UserCommentSummary(comments, user.id).annotate(Mock())
    assert summary.total_user_comments == 1
    assert summary.latest_user_comment == comments[0]
    assert summary.user_comment_counts_by_stage == [0, 0, 0, 1]
    assert summary.complete == True

def test_progress_total_filters_comments():
    user = UserFactory.build(id=1)
    user2 = UserFactory.build(id=2)
    comments = [
        CommentFactory.build(user=user),
        CommentFactory.build(user=user2),
    ]

    summary = UserCommentSummary(comments, user.id).annotate(Mock())
    assert summary.total_user_comments == 1
    assert summary.latest_user_comment == comments[0]

def test_progress_total_latest_comment():
    user = UserFactory.build()
    comments = [
        CommentFactory.build(user=user, created=now() - timedelta(days=1)),
        CommentFactory.build(user=user, created=now()),
    ]
    summary = UserCommentSummary(comments, user.id).annotate(Mock())
    assert summary.latest_user_comment == comments[1]