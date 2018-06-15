from images.models import *
from rest_framework import serializers
from rest_framework import viewsets
from ..models import *

class UploadSerializer(serializers.Serializer):
    filename = serializers.CharField()
    mimetype = serializers.CharField()
    url = serializers.URLField()

    def to_representation(self, obj):
        """
        There's no generic Upload model, so different models
        will have differing representations going back to the frontend
        """
        if isinstance(obj, Image):
            return {
                "type": "image",
                "url": obj.url
            }
        else:
            return {}

    def to_internal_value(self, data):
        """
        Just pass the data through, CommentSerializer will
        use it to create/update models as necessary
        """
        return data

class CommentSerializer(serializers.ModelSerializer):
    upload = UploadSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'lesson_progress', 'text', 'upload')

    def create(self, validated_data):
        upload = validated_data.pop('upload')
        attrs = validated_data

        if 'mimetype' in upload and upload['mimetype'].startswith('image'):
            attrs['upload'] = Image.from_source_with_job(upload['url'])

        comment = Comment.objects.create(**attrs)
        return comment

    def update(self, instance, validated_data):
        upload = validated_data.pop('upload', None)
        attrs = validated_data

        if 'mimetype' in upload and upload['mimetype'].startswith('image'):
            attrs['upload'] = Image.from_source_with_job(upload['url'])

        for attr, val in attrs.items():
            setattr(instance, attr, val)
        instance.save()
        return instance

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.all()
        progress_filter = self.request.query_params.get('progress', None)
        if progress_filter is not None:
            queryset = queryset.filter(lesson_progress_id=progress_filter)
        return queryset

