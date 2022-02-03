"""View module for handling requests about game types"""
from django.forms import ValidationError
from django.http import HttpResponseServerError
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
        games = Game.objects.all()

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
        # Instead of making a new instance of the Game model, the
        # request.data dictionary is passed to the new serializer as
        # the data. The keys on the dictionary must match what
        # is in the fields on the serializer. After creating the
        # serializer instance, call is_valid to make sure the
        # client sent valid data. If the code passes validation,
        # then the save method will add the game to the
        # database and add an id to the serializer.
        
        gamer = Gamer.objects.get(user=request.auth.user)
        try:
            serializer = CreateGameSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(gamer=gamer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games"""
    class Meta:
        model = Game
        fields = "__all__"
        depth = 2


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        # ? Does it matter if 'fields' is a tuple or an array?
        fields = ['id', 'title', 'maker',
                  'number_of_players', 'skill_level', 'game_type']