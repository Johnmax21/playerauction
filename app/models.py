from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)
    purse = models.IntegerField()
    remaining_purse = models.IntegerField(blank=True)
    logo = models.ImageField(upload_to="team_logos/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # If creating new team
            self.remaining_purse = self.purse
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    base_price = models.IntegerField()
    photo = models.ImageField(upload_to="players/")

    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True, blank=True)
    sold_price = models.IntegerField(null=True, blank=True)

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sold", "Sold"),
        ("unsold", "Unsold"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return self.name
class Auction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    current_price = models.IntegerField(default=0)
    current_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        self.pk = 1   # always single row
        super().save(*args, **kwargs)
class BoughtPlayer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    final_price = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} - {self.team.name}"