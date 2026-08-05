import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import  Team, Player    


GROUP_NAME = "auction_room"

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(GROUP_NAME, self.channel_name)
        await self.accept()
        state = await self.get_auction_state()
        await self.send(text_data=json.dumps(state))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_NAME, self.channel_name)

    async def auction_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_auction_state(self):
        player = Player.objects.filter(is_current=True).select_related("current_bid_team").first()

        teams_data = []
        for team in Team.objects.all():
            players = Player.objects.filter(team=team, status="sold")
            teams_data.append({
                "name": team.name,
                "purse": team.remaining_purse,
                "squad_size": players.count(),
                "players": [{"name": p.name, "position": p.position, "sold_price": p.sold_price} for p in players],
            })

        # moved OUTSIDE the teams loop — build once, not once-per-team
        sold_history = []
        sold_players = Player.objects.filter(status="sold").select_related("team").order_by("-id")
        for p in sold_players:
            sold_history.append({
                "name": p.name,
                "price": p.sold_price,
                "team": p.team.name if p.team else "",
            })

        if not player:
            return {
                "player": "", "role": "", "player_image": "",
                "auction": {"status": "", "base_price": 0, "current_bid": 0, "sold_team": ""},
                "teams": teams_data,
                "sold_history": sold_history,   # added
            }

        if player.status == "sold":
            status = "SOLD"
        elif player.status == "unsold":
            status = "UNSOLD"
        else:
            status = ""

        return {
            "player": player.name,
            "role": player.position,
            "player_image": player.photo.url if player.photo else "",
            "auction": {
                "status": status,
                "base_price": player.base_price,
                "current_bid": player.current_bid_price or player.base_price,
                "sold_team": player.current_bid_team.name if player.current_bid_team else "",
            },
            "teams": teams_data,
            "sold_history": sold_history,   # added
        }

    async def display_mode_update(self, event):
        await self.send(text_data=json.dumps({"display_mode": event["mode"]}))
    async def ticker_visibility_update(self, event):
        await self.send(text_data=json.dumps({
            "ticker_visibility": {"ticker": event["ticker"], "visible": event["visible"]}
        }))