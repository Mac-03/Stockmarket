from django.db import models
from django.contrib.auth.models import User  # Assuming you're using Django's built-in user model

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    stock_name = models.CharField(max_length=255)
    target_price = models.FloatField()
    stop_loss_price = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_name} for {self.user.username}"

