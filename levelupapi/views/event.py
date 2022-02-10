"""View module for handling requests about game types"""
from django.forms import ValidationError
from django.http import HttpResponseServerError
from django.db.models import Count, Q
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from levelupapi.models import Event, Game, Gamer


class EventView(ViewSet):
    """Level Up Events view"""

    def retrieve(self, request, pk):
        """Handles the GET requests for a single event

        Returns:
            Response: JSON serialized event
        """
        gamer = Gamer.objects.get(user=request.auth.user)

        try:
            event = Event.objects.annotate(
                attendees_count=Count('attendees'), joined=Count(
                    'attendees',
                    filter=Q(attendees=gamer)
                )).get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET requests for all events

        Returns:
            Response: JSON serialized event
        """
        # events = Event.objects.all()
        # events = Event.objects.annotate(attendees_count=Count('attendees'))

        gamer = Gamer.objects.get(user=request.auth.user)

        events = Event.objects.annotate(
            attendees_count=Count('attendees'),
            joined=Count(
                'attendees',
                filter=Q(attendees=gamer)
            )
        )

        game_param = request.query_params.get('game', None)

        if game_param is not None:
            events = events.filter(game_id=game_param)

        serializer = EventSerializer(events, many=True)

        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized event instance
        """
        organizer = Gamer.objects.get(user=request.auth.user)

        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(organizer=organizer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """

        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        organizer = Gamer.objects.get(pk=request.data['organizer'])
        game = Game.objects.get(pk=request.data["game"])
        event.organizer = organizer
        event.game = game
        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        """Handles the DELETE requests for events

        Args:
            request (object): the object to delete
            pk (integer): the primary key on the object

        Returns:
            response: 204 no content
        """
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    # * Using the action decorator turns a method into a new route
    # * In this case, the action will accept POST methods, and because detail=True the url will include the pk
    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
        # Need to get the current gamer and the event they want to sign up for
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        # Now we need to append the gamer to the attendees list on the event
        event.attendees.add(gamer)
        # Finally return the 201 status code
        return Response({'message': 'Gamer added to event'}, status=status.HTTP_201_CREATED)

    # Write a new method named leave
    # It should have the action decorator
    # It should accept DELETE requests
    # It should be a detail route
    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to be removed from an event"""
        # Get the gamer and the event objects
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
    # Use the remove method on the ManyToManyField to delete the gamer from the join table
        event.attendees.remove(gamer)
    # Return a 204 Response
        return Response({'message': 'Gamer removed from event'})
    # Test in Postman by sending a DELETE request to http://localhost:8000/events/12/leave


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    attendees_count = serializers.IntegerField(default=None)

    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'organizer',
                  'date', 'time', 'attendees', 'joined', 'attendees_count')
        depth = 1


class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        # ? Does it matter if 'fields' is an array or a tuple?
        fields = ['id', 'game', 'description',
                  'date', 'time', 'organizer']
