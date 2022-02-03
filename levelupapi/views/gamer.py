"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Gamer


class GamerView(ViewSet):
    """Level Up gamer view"""

    def retrieve(self, request, pk):
        try:
            gamer = Gamer.objects.get(pk=pk)
            serializer = GamerSerializer(gamer)
            return Response(serializer.data)
        except Gamer.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        gamers = Gamer.objects.all()
        serializer = GamerSerializer(gamers, many=True)
        return Response(serializer.data)


class GamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamer
        fields = "__all__"
        depth = 1
