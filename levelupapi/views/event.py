"""View module for handling requests about game types"""
from django.forms import ValidationError
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Game, Gamer


class EventView(ViewSet):
    """Level Up Events view"""

    def retrieve(self, request, pk):
        """Handles the GET requests for a single event

        Returns:
            Response: JSON serialized event
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET requests for all events

        Returns:
            Response: JSON serialized event
        """
        events = Event.objects.all()

        game = request.query_params.get('game', None)

        if game is not None:
            events = events.filter(game_id=game)

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized event instance
        """
        # Instead of making a new instance of the Event model, the
        # request.data dictionary is passed to the new serializer as
        # the data.
        #
        # The keys on the dictionary must match what
        # is in the fields on the serializer.
        #
        # After creating the serializer instance, call is_valid to make
        # sure the client sent valid data.
        #
        # If the code passes validation, then the save method
        # will add the event to the database and add an id to
        # the serializer.

        organizer = Gamer.objects.get(user=request.auth.user)
        try:
            serializer = CreateEventSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(organizer=organizer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    class Meta:
        model = Event
        fields = "__all__"
        depth = 2


class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        # ? Does it matter if 'fields' is an array or a tuple?
        fields = ['id', 'game', 'description',
                  'date', 'time', 'organizer']
