from django.contrib.auth import get_user_model
from functools import reduce
from images.models import *
from rest_framework import serializers
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
        fields = ('id', 'author', 'lesson_progress', 'text', 'upload', 'role')

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

def option_representations(obj, q_idx, result=None):
    idx = 1
    while getattr(obj, "answer_%d_%d" % (q_idx, idx), None):
        data = {
            "text": getattr(obj, "answer_%d_%d" % (q_idx, idx)),
            "selected": False
        }
        if result:
            data["selected"] = getattr(result, "answer_%d" % q_idx) == idx

        yield data

        idx += 1

def question_representations(obj, result=None):
    idx = 1
    while getattr(obj, "question_%d" % idx, None):
        data = {
            "answered": False,
            "text": getattr(obj, "question_%d" % idx),
            "options": list(option_representations(obj, idx, result=result))
        }
        if result:
            data["answered"] = True
            correct = getattr(result, "answer_%d" % idx) == getattr(obj, "correct_answer_%d" % idx)
            data["correct"] = correct
            if correct:
                data["explanation"] = getattr(obj, "explanation_%d" % idx)

        yield data

        idx += 1

def answer_representations(obj):
    idx = 1
    while getattr(obj, "answer_%d" % idx, None):
        yield getattr(obj, "answer_%d" % idx)
        idx += 1

class QuizSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            "answered": False,
            "questions": list(question_representations(obj)),
            "answers": []
        }

class QuizAndResultSerializer(serializers.Serializer):

    def to_representation(self, obj):
        data = {
            "answered": True,
            "questions": list(question_representations(obj.quiz, result=obj)),
            "answers": list(answer_representations(obj))
        }
        data["correct"] = reduce(lambda a, b: a and b, map(lambda x: x["correct"], data["questions"]))
        return data

class QuizResultSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child = serializers.IntegerField()
    )
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    taker = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    def to_representation(self, instance):
        answers = []
        idx = 1
        while getattr(instance, "answer_%d" % idx, None):
            answers.append(getattr(instance, "answer_%d" % idx))
            idx += 1

        return {
            "quiz": instance.quiz_id,
            "taker": instance.taker_id,
            "answers": answers
        }

    def create(self, validated_data):
        result = QuizResult(quiz=validated_data['quiz'], taker=validated_data['taker'])
        for idx, answer in enumerate(validated_data['answers']):
            setattr(result, "answer_%d" % (idx + 1), answer)
        result.save()
        return result

