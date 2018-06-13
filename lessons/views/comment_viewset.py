from rest_framework import serializers
from rest_framework import viewsets
from ..models import *

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'source_url', 'url')
        read_only_fields = ('url', )

class CommentSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'lesson_progress', 'text', 'image')

    def create(self, validated_data):
        image_src = validated_data['image']['source_url']
        image = Image.from_source_with_job(image_src) if image_src else None
        validated_data.pop('image')
        comment = Comment.objects.create(image=image, **validated_data)
        return comment

    def update(self, instance, validated_data):
        if 'image' in validated_data:
            image_src = validated_data['image']['source_url']
            instance.image = Image.from_source_with_job(image_src)
        validated_data.pop('image', None)
        for attr, val in validated_data.items():
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

