from django.db import models

class Test(models.Model):
     test_id = models.CharField(max_length=256, unique=True)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return '{} - ran on {}'.format(self.test_id, self.created_at)
     
     class Meta:
          ordering = ['-created_at']

class StoredPacket(models.Model):
     header = models.CharField(max_length=256)
     timestamp = models.FloatField()
     values = models.JSONField() 
     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="packets")

     def __str__(self):
          return '{} - at {}'.format(self.header, self.timestamp)