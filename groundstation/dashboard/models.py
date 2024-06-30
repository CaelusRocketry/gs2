from django.db import models


class Test(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Test ran on {}".format(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class StoredPacket(models.Model):
    header = models.CharField(max_length=256)
    timestamp = models.FloatField()
    values = models.JSONField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="packets")

    def __str__(self):
        return "{} - at {}".format(self.header, self.timestamp)
