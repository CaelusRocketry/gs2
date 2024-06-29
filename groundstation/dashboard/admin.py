from django.contrib import admin
from .models import Test, StoredPacket

# Register your models here.
admin.site.register(Test)
admin.site.register(StoredPacket)
