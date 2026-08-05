from django.urls import path
from . import views

urlpatterns = [
    path("control/", views.control, name="control"),
    path("", views.display_page, name="display_page"),
    path("home/",views.home, name="home"),

    path("bid/<int:auction_id>/", views.place_bid, name="place_bid"),
    path("get-auction/", views.get_auction, name="get_auction"),
    # path("sell/<int:auction_id>/", views.sell_player, name="sell_player"),
    path("addplayer/", views.add_player, name="add_player"),
    path("set-player/", views.set_player, name="set_player"),
    path("teams/", views.team_page, name="team_page"),
    path("place-bid/", views.place_bid, name="place_bid"),
# path("sell-player/", views.sell_player, name="sell_player"),
path("unsold-player/", views.unsold_player, name="unsold_player"),
path("mark-sold/", views.mark_sold, name="mark_sold"),
path("manual-bid/", views.manual_bid, name="manual_bid"),
path("set-display-mode/", views.set_display_mode, name="set_display_mode"),
path("set-ticker-visibility/", views.set_ticker_visibility, name="set_ticker_visibility"),

]