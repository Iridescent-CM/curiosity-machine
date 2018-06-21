from rest_framework import serializers
from images.models import *
from videos.models import *
from .models import *

class UploadSerializer(serializers.Serializer):
    filename = serializers.CharField()
    mimetype = serializers.CharField()
    url = serializers.URLField()

    def to_image_representation(self, obj):
        return {
            "type": "image",
            "url": obj.url
        }

    def to_video_representation(self, obj):
        thumb = obj.thumbnails.first()
        data = {
            "type": "video",
            "url": obj.url,
            "encodings": [],
            "thumbnail": thumb.url if thumb else ""
        }
        for encoding in obj.encoded_videos.all():
            data['encodings'].append({
                "url": encoding.url,
                "mimetype": encoding.mime_type
            })
        return data


    def to_representation(self, obj):
        """
        There's no generic Upload model, so different models
        will have differing representations going back to the frontend
        """
        funcname = "to_%s_representation" % obj.__class__.__name__.lower()
        if hasattr(self, funcname):
            return getattr(self, funcname)(obj)
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

    def _handle_media(self, attrs, upload):
        if upload and 'mimetype' in upload:
            mimetype = upload['mimetype']
            if mimetype.startswith('image'):
                attrs['upload'] = Image.from_source_with_job(upload['url'])
            elif mimetype.startswith('video'):
                attrs['upload'] = Video.from_source_with_job(upload['url'])

        return attrs

    def create(self, validated_data):
        upload = validated_data.pop('upload')
        attrs = validated_data
        attrs = self._handle_media(attrs, upload)

        comment = Comment.objects.create(**attrs)
        return comment

    def update(self, instance, validated_data):
        upload = validated_data.pop('upload', None)
        attrs = validated_data
        attrs = self._handle_media(attrs, upload)

        for attr, val in attrs.items():
            setattr(instance, attr, val)
        instance.save()
        return instance

