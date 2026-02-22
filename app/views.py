from django.shortcuts import render
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Player, Team, Auction, BoughtPlayer

def control(request):
    auction = Auction.objects.first()
    players = Player.objects.all()
    teams = Team.objects.all()

    return render(request, "control.html", {
        "auction": auction,
        "players": players,
        "teams": teams
    })

def display_page(request):
    auction = Auction.objects.filter(is_active=True).first()

    return render(request, "display.html", {
        "auction": auction
    })
from django.http import JsonResponse
from .models import Auction

from django.http import JsonResponse
from .models import Auction

def get_auction(request):
    auction = Auction.objects.order_by('-id').first()

    if not auction:
        return JsonResponse({
            "player": "",
            "price": 0,
            "team": None,
            "is_sold": False
        })

    return JsonResponse({
        "player": auction.player.name if auction.player else "",
        "price": auction.current_price,
        "team": auction.current_team.name if auction.current_team else None,
        "is_sold": auction.is_sold  # MUST be boolean
    })
from django.http import JsonResponse
import json

def place_bid(request):
    import json
    data = json.loads(request.body)
    team_id = data.get("team_id")

    if not team_id:
        return JsonResponse({"error": "No team selected"})

    if not team_id.isdigit():
        return JsonResponse({"error": "Invalid team ID"})

    auction = Auction.objects.first()
    team = Team.objects.get(id=int(team_id))

    if not auction or not auction.player:
        return JsonResponse({"error": "No active auction"})

    new_price = auction.current_price + 50

    if team.remaining_purse < new_price:
        return JsonResponse({"error": "Insufficient purse"})

    auction.current_price = new_price
    auction.current_team = team
    auction.save()

    return JsonResponse({
        "price": auction.current_price,
        "team": team.name
    })
def sell_player(request):
    auction = Auction.objects.first()
    player = auction.player
    team = auction.current_team
    price = auction.current_price

    if player and team:
        player.team = team
        player.sold_price = price
        player.status = "sold"
        player.save()

        team.remaining_purse -= price
        team.save()

    # Reset auction
    auction.player = None
    auction.current_price = 0
    auction.current_team = None
    auction.save()

    return JsonResponse({"status": "sold"})

def unsold_player(request):
    auction = Auction.objects.first()
    player = auction.player

    if player:
        player.status = "unsold"
        player.save()

    auction.player = None
    auction.current_price = 0
    auction.current_team = None
    auction.save()

    return JsonResponse({"status": "unsold"})


from django.shortcuts import render, redirect
from .models import Player

def add_player(request):
    if request.method == "POST":
        name = request.POST.get("name")
        position = request.POST.get("position")
        base_price = request.POST.get("base_price")
        photo = request.FILES.get("photo")

        Player.objects.create(
            name=name,
            position=position,
            base_price=base_price,
            photo=photo
        )

        return redirect("add_player")

    return render(request, "add_player.html")


from django.http import JsonResponse
import json

def set_player(request):
    import json
    data = json.loads(request.body)
    player_id = data.get("player_id")

    if not player_id:
        return JsonResponse({"error": "No player selected"})

    player = Player.objects.get(id=player_id)

    # Get or create auction
    auction, created = Auction.objects.get_or_create(
        id=1,
        defaults={
            "player": player,
            "current_price": player.base_price
        }
    )

    # If already exists, update it
    auction.player = player
    auction.current_price = player.base_price
    auction.current_team = None
    auction.save()

    return JsonResponse({"success": True})
    

def team_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        purse = request.POST.get("purse")
        logo = request.FILES.get("logo")

        Team.objects.create(
            name=name,
            purse=purse,
            logo=logo
        )

    teams = Team.objects.all()

    return render(request, "team.html", {
        "teams": teams
    })

from django.http import JsonResponse
from .models import Auction

import json
from django.http import JsonResponse
from .models import Auction

def mark_sold(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    data = json.loads(request.body)
    player_id = data.get("player_id")

    if not player_id:
        return JsonResponse({"error": "Player ID missing"})

    auction = Auction.objects.get(
        id=player_id    )
    print(player_id)

    if not auction:
        return JsonResponse({"error": "No active auction found"})

    if not auction.current_team:
        return JsonResponse({"error": "No bids placed yet"})

    team = auction.current_team

    # Deduct purse
    team.remaining_purse -= auction.current_price
    team.save()

    # Close auction
    auction.is_active = False
    auction.is_sold = True
    auction.save()

    return JsonResponse({
        "success": True,
        "team": team.name,
        "price": auction.current_price
    })