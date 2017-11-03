from rest_framework import serializers
from cmcomments.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    challenge_progress_id = serializers.ReadOnlyField(source='challenge_progress.id')
    user_id = serializers.ReadOnlyField(source='user.id')
    user_role = serializers.ReadOnlyField(source='user.extra.role')
    class Meta:
        model = Comment
        fields = ('challenge_progress_id', 'user_id', 'created', 'stage', 'user_role')