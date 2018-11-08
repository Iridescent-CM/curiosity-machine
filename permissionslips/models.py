from django.contrib.auth import get_user_model
from django.db import models

class PermissionSlip(models.Model):
    signature = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(get_user_model())

    def __str__(self):
        return "PermissionSlip: id=%s account=%s" % (self.id, self.account)
