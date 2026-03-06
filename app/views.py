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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Auction, Team
import json
def place_bid(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"})

    team_id = data.get("team_id")
    player_id = data.get("player_id")
    print(f"Received player_id: {player_id}, team_id: {team_id}")  # Debug: What ID is actually sent?
    if not team_id or not player_id:
        return JsonResponse({"error": "Missing data"})

    try:
        team = Team.objects.get(id=int(team_id))
        player = Player.objects.get(id=int(player_id))
        print(player.name)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found"})
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"})

    # ✅ Manual get or create
    auction = Auction.objects.filter(player=player).first()

    if not auction:
        auction = Auction(
            player=player,
            current_price=player.base_price,
            current_team=None
        )
        auction.save()

    increment = 50
    new_price = auction.current_price + increment

    if team.remaining_purse < new_price:
        return JsonResponse({"error": "Insufficient purse"})

    auction.current_price = new_price
    auction.current_team = team
    auction.save()

    return JsonResponse({
        "price": auction.current_price,
        "team": team.name
    })
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Auction, Player, Team  # Adjust imports

# @csrf_exempt  # If not using CSRF in POST
# def sell_player(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request method"})

#     try:
#         data = json.loads(request.body)
#         player_id = data.get("player_id")
#     except:
#         return JsonResponse({"error": "Invalid JSON"})

#     if not player_id:
#         return JsonResponse({"error": "Missing player_id"})

#     try:
#         player = Player.objects.get(id=int(player_id))
#         auction = Auction.objects.get(player=player)  # Get specific player's Auction
#     except Player.DoesNotExist:
#         return JsonResponse({"error": "Player not found"})
#     except Auction.DoesNotExist:
#         return JsonResponse({"error": "No auction for this player"})

#     team = auction.current_team
#     price = auction.current_price

#     if player and team:
#         player.team = team
#         player.sold_price = price
#         player.status = "sold"
#         player.save()

#         team.remaining_purse -= price
#         team.save()

#         # Reset this specific Auction
#         auction.player = None
#         auction.current_price = 0
#         auction.current_team = None
#         auction.status = "completed"  # Optional: Add status field to model
#         auction.save()

#     return JsonResponse({
#         "status": "sold",
#         "player": player.name,
#         "team": team.name if team else "None",
#         "price": price
#     })
from django.http import JsonResponse
from .models import Auction
import json

def unsold_player(request):
   

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"})

    player_id = data.get("player_id")

    if not player_id or not str(player_id).isdigit():
        return JsonResponse({"error": "Invalid player ID"})

    try:
        auction = Auction.objects.get(id=int(player_id))
    except Auction.DoesNotExist:
        return JsonResponse({"error": "Auction not found"})

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

from django.http import JsonResponse
import json

def set_player(request):
    if request.method == "POST":
        data = json.loads(request.body)
        player_id = data.get("player_id")

        player = Player.objects.get(id=player_id)

        return JsonResponse({
            "player": player.name,
            "price": player.base_price,
            "team": player.team.name if player.team else None
        })
    

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

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # If not already using
from .models import Auction, Player, Team  # Adjust import as needed

@csrf_exempt  # Or handle CSRF in middleware
def mark_sold(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"})

    player_id = data.get("player_id")
    if not player_id:
        return JsonResponse({"error": "Player ID missing"})

    try:
        player = Player.objects.get(id=int(player_id))
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"})

    # ✅ Fetch Auction by player (like in place_bid)
    auction = Auction.objects.filter(player=player).first()
    if not auction:
        return JsonResponse({"error": "No active auction found"})

    if not auction.current_team:
        return JsonResponse({"error": "No bids placed yet"})

    team = auction.current_team

    # Deduct purse (only if not already deducted—add a check if needed)
    if team.remaining_purse < auction.current_price:
        return JsonResponse({"error": "Team has insufficient purse (already deducted?)"})
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

def manual_bid(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    data = json.loads(request.body)

    player_id = data.get("player_id")
    team_id = data.get("team_id")
    price = data.get("price")

    if not player_id or not team_id or not price:
        return JsonResponse({"error": "Missing data"})

    try:
        player = Player.objects.get(id=player_id)
        team = Team.objects.get(id=team_id)
        price = int(price)

    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"})

    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found"})

    auction = Auction.objects.filter(player=player).first()

    if not auction:
        auction = Auction(
            player=player,
            current_price=player.base_price
        )

    if price <= auction.current_price:
        return JsonResponse({"error": "Bid must be higher than current price"})

    if team.remaining_purse < price:
        return JsonResponse({"error": "Insufficient purse"})

    auction.current_price = price
    auction.current_team = team
    auction.save()

    return JsonResponse({
        "price": auction.current_price,
        "team": team.name
    })