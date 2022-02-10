from django.db import models
from levelupapi.models.event import Event

from django.db import models


class EventGamer(models.Model):
    gamer = models.ForeignKey("Gamer", on_delete=models.CASCADE, related_name="attendees")
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
