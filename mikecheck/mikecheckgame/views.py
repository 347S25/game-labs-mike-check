from django.views import generic
from django.shortcuts import get_object_or_404, render
from .models import GameState, Player, Game
import json


# Create your views here.
def index(request):

    if request.method == "POST":
        print("VERB:", request.POST.get("verb"))

    # p = Player.objects.first()
    # g = Game.objects.last()
    # gp = g.creator
    # gamestate = g.get_active_state()
    # game_board = []

    # for j in range(g.height):
    #     row = []
    #     for i in range(g.width):
    #         b = gamestate.get_board(i, j)
    #         row.append(b.board_state.get("marks"))
    #     game_board.append(row)

    context = {
        # "gameplayer": gp,
        # "game": g,
        # "board": game_board,
        # "gid": g.id,
        # "gsid": gamestate.id,
    }

    return render(request, "index.html", context=context)


def observe(request, game_id):
    # p = Player.objects.first()
    g = get_object_or_404(Game, id=game_id)
    gp = g.creator
    gamestate = g.get_active_state()
    game_board = []

    for j in range(g.height):
        row = []
        for i in range(g.width):
            b = gamestate.get_board(i, j)
            row.append(b.board_state.get("marks"))
        game_board.append(row)

    context = {
        "gameplayer": gp,
        "game": g,
        "board": game_board,
        "gid": g.id,
        "gsid": gamestate.id,
    }
    return render(request, "observe.html", context=context)


def take_turn(request, game_id):
    g = get_object_or_404(Game, id=game_id)
    gp = g.creator
    gamestate = g.get_active_state()
    game_board = []
    if request.method == "POST":
        # FIXME: it won't always be g.creator==gp here
        gamestate = GameState.objects.from_data(g, gp, request.POST)

    for j in range(g.height):
        row = []
        for i in range(g.width):
            b = gamestate.get_board(i, j)
            bs = b.board_state.get("marks")
            with_pos = {"x": i, "y": j, "marks": bs}
            row.append(with_pos)
        game_board.append(row)

    context = {
        "gameplayer": gp,
        "game": g,
        "board": game_board,
        "gid": g.id,
        "gsid": gamestate.id,
    }
    return render(request, "take_turn.html", context=context)


class GameListView(generic.ListView):
    model = Game
    paginate_by = 10
