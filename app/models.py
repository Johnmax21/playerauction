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

    # final result (after sold)
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True, blank=True)
    sold_price = models.IntegerField(null=True, blank=True)

    # NEW — needed to replace what Auction was doing during live bidding
    is_current = models.BooleanField(default=False)       # replaces "is_active" — marks the ONE player currently on stage
    current_bid_price = models.IntegerField(null=True, blank=True)   # replaces auction.current_price
    current_bid_team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True, blank=True, related_name="bidding_on")  # replaces auction.current_team

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sold", "Sold"),
        ("unsold", "Unsold"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")