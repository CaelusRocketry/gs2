from django.db import models


class Test(models.Model):
    ENVIRONMENTS = [
        ("xbee", "XBee"),
        ("sim", "Simulation"),
        ("bt", "Bluetooth")
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    environment = models.CharField(max_length=24, choices=ENVIRONMENTS)

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
