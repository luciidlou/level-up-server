from django.db import models


class Event(models.Model):
    @property
    def joined(self):   # pylint: disable=missing-function-docstring
        return self.__joined

    @joined.setter
    def joined(self, value):
        self.__joined = value

    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="events")
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    organizer = models.ForeignKey(
        "Gamer", on_delete=models.CASCADE, related_name="organizing")
    attendees = models.ManyToManyField(
        "Gamer", through="EventGamer", related_name="attending")
