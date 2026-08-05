<<<<<<< HEAD
import json
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Player, Team
from .consumers import GROUP_NAME


def home(request):
    return render(request, "home.html")


def broadcast_auction_update():
    """Call this after ANY change to Player auction state."""
    from .consumers import AuctionConsumer
    channel_layer = get_channel_layer()
    consumer = AuctionConsumer()
    state = async_to_sync(consumer.get_auction_state)()
    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {"type": "auction_update", "data": state},
    )


def control(request):
    current_player = Player.objects.filter(is_current=True).first()
    players = Player.objects.filter(status="pending")
    teams = Team.objects.all()
    return render(request, "control.html", {
        "auction": current_player,
=======
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
>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f
        "players": players,
        "teams": teams
    })

<<<<<<< HEAD

def display_page(request):
    current_player = Player.objects.filter(is_current=True).first()
    return render(request, "display.html", {"auction": current_player})


def get_auction(request):
    """Kept for initial page-load / fallback; consumer handles live updates now."""
    player = Player.objects.filter(is_current=True).first()
    if not player:
        return JsonResponse({"player": "", "price": 0, "team": None, "is_sold": False})
    return JsonResponse({
        "player": player.name,
        "price": player.current_bid_price or player.base_price,
        "team": player.current_bid_team.name if player.current_bid_team else None,
        "is_sold": player.status == "sold",
    })


@csrf_exempt
def set_player(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"})

    player_id = data.get("player_id")
    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"})

    Player.objects.filter(is_current=True).update(is_current=False)

    player.is_current = True
    player.current_bid_price = player.base_price
    player.current_bid_team = None
    player.status = "pending"
    player.save()

    broadcast_auction_update()
    return JsonResponse({"player": player.name, "price": player.current_bid_price})


@csrf_exempt
def place_bid(request):
=======
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
    
>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    try:
        data = json.loads(request.body)
<<<<<<< HEAD
    except json.JSONDecodeError:
=======
    except:
>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f
        return JsonResponse({"error": "Invalid JSON"})

    team_id = data.get("team_id")
    player_id = data.get("player_id")
<<<<<<< HEAD
=======
    print(f"Received player_id: {player_id}, team_id: {team_id}")  # Debug: What ID is actually sent?
>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f
    if not team_id or not player_id:
        return JsonResponse({"error": "Missing data"})

    try:
        team = Team.objects.get(id=int(team_id))
<<<<<<< HEAD
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found"})

    with transaction.atomic():
        try:
            player = Player.objects.select_for_update().get(id=int(player_id))
        except Player.DoesNotExist:
            return JsonResponse({"error": "Player not found"})

        if player.status == "sold":
            return JsonResponse({"error": "This player has already been sold"})

        new_price = (player.current_bid_price or player.base_price) + 50
        if team.remaining_purse < new_price:
            return JsonResponse({"error": "Insufficient purse"})

        player.current_bid_price = new_price
        player.current_bid_team = team
        player.save()

    broadcast_auction_update()
    return JsonResponse({"price": player.current_bid_price, "team": team.name})


@csrf_exempt
def manual_bid(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"})

    team_id = data.get("team_id")
    price = data.get("price")
    if not team_id or not price:
        return JsonResponse({"error": "Missing data"})

    try:
        team = Team.objects.get(id=team_id)
        price = int(price)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found"})
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid price"})

    with transaction.atomic():
        player = Player.objects.select_for_update().filter(is_current=True).first()
        if not player:
            return JsonResponse({"error": "No active auction found"})
        if player.status == "sold":
            return JsonResponse({"error": "This player has already been sold"})

        current = player.current_bid_price or player.base_price
        if price <= current:
            return JsonResponse({"error": "Bid must be higher than current price"})
        if team.remaining_purse < price:
            return JsonResponse({"error": "Insufficient purse"})

        player.current_bid_price = price
        player.current_bid_team = team
        
        player.save()

    broadcast_auction_update()
    return JsonResponse({"price": player.current_bid_price, "team": team.name})


@csrf_exempt
def mark_sold(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    with transaction.atomic():
        player = Player.objects.select_for_update().filter(is_current=True).first()
        if not player:
            return JsonResponse({"error": "No active auction found"})
        if player.status == "sold":
            return JsonResponse({"error": "This player has already been sold"})
        if not player.current_bid_team:
            return JsonResponse({"error": "No bids placed yet"})

        team = player.current_bid_team
        if team.remaining_purse < player.current_bid_price:
            return JsonResponse({"error": "Team has insufficient purse"})

        team.remaining_purse -= player.current_bid_price
        team.save()

        player.team = team
        player.sold_price = player.current_bid_price
        player.status = "sold"
        player.save()

    broadcast_auction_update()
    return JsonResponse({"success": True, "team": team.name, "price": player.sold_price})


@csrf_exempt
def unsold_player(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    player = Player.objects.filter(is_current=True).first()
    if not player:
        return JsonResponse({"error": "No active auction found"})

    player.status = "unsold"
    player.team = None
    player.sold_price = None
    player.current_bid_price = None
    player.current_bid_team = None

    player.save()

    broadcast_auction_update()
    return JsonResponse({"status": "unsold"})


@csrf_exempt
def set_display_mode(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"})

    mode = data.get("mode", "auction")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {"type": "display_mode_update", "mode": mode},
    )
    return JsonResponse({"mode": mode})

=======
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
>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f

def add_player(request):
    if request.method == "POST":
        name = request.POST.get("name")
        position = request.POST.get("position")
        base_price = request.POST.get("base_price")
        photo = request.FILES.get("photo")
<<<<<<< HEAD
        Player.objects.create(name=name, position=position, base_price=base_price, photo=photo)
        return redirect("add_player")
    return render(request, "add_player.html")


=======

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
    

>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f
def team_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        purse = request.POST.get("purse")
        logo = request.FILES.get("logo")
<<<<<<< HEAD
        Team.objects.create(name=name, purse=purse, logo=logo)
    teams = Team.objects.all()
    return render(request, "team.html", {"teams": teams})
@csrf_exempt
def set_ticker_visibility(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"})

    ticker = data.get("ticker")       # "team" or "sold"
    visible = data.get("visible")     # true/false

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {"type": "ticker_visibility_update", "ticker": ticker, "visible": visible},
    )
    return JsonResponse({"ok": True})
=======

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
>>>>>>> 7cf366cb84cba0c0713aee311783559d641c922f
