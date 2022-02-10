"""View module for handling requests about game types"""
from email.policy import default
from django.forms import ValidationError
from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Game, Gamer, GameType


class GameView(ViewSet):
    """Level Up game views"""

    def retrieve(self, request, pk):
        """Handles the GET requests for a single game

        Returns:
            Response: JSON serialized event
        """
        try:
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game)
            return Response(serializer.data)
        except Game.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET requests for all games

        Returns:
            Response: JSON serialized event
        """
        # games = Game.objects.all()
        games = Game.objects.annotate(event_count=Count('events'))

        game_type = request.query_params.get('type', None)

        if game_type is not None:
            games = games.filter(game_type_id=game_type)

        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        try:
            serializer = CreateGameSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(gamer=gamer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """

        game = Game.objects.get(pk=pk)
        game.title = request.data["title"]
        game.maker = request.data["maker"]
        game.number_of_players = request.data["number_of_players"]
        game.skill_level = request.data["skill_level"]

        game_type = GameType.objects.get(pk=request.data["game_type"])
        game.game_type = game_type
        game.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        """Handles DELETE requests for a game

        Args:
            request (object): the object we want to delete
            pk (integer): the primary key on the object

        Returns:
            response: 204 no content
        """
        game = Game.objects.get(pk=pk)
        game.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for retrieveing games"""
    event_count = serializers.IntegerField(default=None)
    class Meta:
        model = Game
        fields = "__all__"
        depth = 2


class CreateGameSerializer(serializers.ModelSerializer):
    """JSON serializer for creating games"""
    class Meta:
        model = Game
        fields = ['id', 'title', 'maker',
                  'number_of_players', 'skill_level', 'game_type']
