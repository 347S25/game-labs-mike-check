import random
from django.contrib.auth.models import User
from django.db import models
from django.http import QueryDict
from django.urls import reverse

JOIN_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ346789abdgjmnpqrt"
JOIN_CODE_LENGTH = 6

WIDTH = 3
HEIGHT = 3
WIN_LENGTH = 3
SUB_WIDTH = 3
SUB_HEIGHT = 3
SUB_WIN_LENGTH = 3


def generate_join_code():
    code = "".join(random.choice(JOIN_CODE_CHARS) for _ in range(JOIN_CODE_LENGTH))
    while Game.objects.filter(join_code=code).exists():
        code = "".join(random.choice(JOIN_CODE_CHARS) for _ in range(JOIN_CODE_LENGTH))
    return code


class Player(models.Model):
    handle = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.user:
            return self.user.username
        return self.handle


class GamePlayer(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    mark = models.CharField(max_length=8, blank=True)


class GameManager(models.Manager):
    def create_game(self, creator: GamePlayer) -> "Game":
        g = self.model(creator=creator)
        g.save()
        gs = GameState.objects.create_gamestate(g, creator)
        return g


class Game(models.Model):
    creator = models.ForeignKey(
        GamePlayer, on_delete=models.CASCADE, related_name="games"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    join_code = models.CharField(
        max_length=JOIN_CODE_LENGTH, default=generate_join_code, unique=True
    )
    width = models.IntegerField(default=WIDTH)
    height = models.IntegerField(default=HEIGHT)
    win_length = models.IntegerField(default=WIN_LENGTH)
    sub_width = models.IntegerField(default=SUB_WIDTH)
    sub_height = models.IntegerField(default=SUB_HEIGHT)
    sub_win_length = models.IntegerField(default=SUB_WIN_LENGTH)
    objects = GameManager()

    def get_active_state(self):
        state = self.gamestate_set.all().order_by("-created_at").first()
        return state

    def __str__(self):
        return f"{self.creator}'s {self.width}x{self.height} of {self.sub_width}x{self.sub_height}s from {self.created_at}"

    def get_absolute_url(self):
        return reverse("take_turn", args=[str(self.id)])


class BoardManager(models.Manager):
    def create_board(self, gamestate: "GameState", x: int, y: int) -> "Board":
        b = self.model(gamestate=gamestate, x=x, y=y)
        b.save()
        bs = {}
        marks = []
        for j in range(gamestate.game.sub_height):
            row = []
            for i in range(gamestate.game.sub_width):
                row.append("")
            marks.append(row)
        bs["marks"] = marks
        b.board_state = bs
        b.save()
        return b

    def from_data(
        self, gamestate: "GameState", x: int, y: int, data: QueryDict
    ) -> "Board":
        b = self.model(gamestate=gamestate, x=x, y=y)
        b.save()
        bs = {}
        marks = []
        for j in range(gamestate.game.sub_height):
            row = []
            for i in range(gamestate.game.sub_width):
                row.append(data.get(f"board-{y}-{x}--entry-{j}-{i}"))
            marks.append(row)
        bs["marks"] = marks
        b.board_state = bs
        b.save()
        return b


class Board(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    gamestate = models.ForeignKey("GameState", on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    winner = models.ForeignKey(
        GamePlayer, on_delete=models.CASCADE, null=True, blank=True
    )
    objects = BoardManager()
    board_state = models.JSONField(default=dict)


class GameStateManager(models.Manager):
    def create_gamestate(self, game: Game, creator: GamePlayer) -> "GameState":
        gs = self.model(game=game, creator=creator)
        gs.save()
        for j in range(game.height):
            for i in range(game.width):
                Board.objects.create_board(gs, i, j)
        return gs

    def from_data(
        self, game: Game, creator: GamePlayer, data: QueryDict
    ) -> "GameState":
        gs = self.model(game=game, creator=creator)
        gs.save()
        for j in range(game.height):
            for i in range(game.width):
                Board.objects.from_data(gs, i, j, data)
        return gs


class GameState(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    creator = models.ForeignKey(
        GamePlayer, on_delete=models.CASCADE, related_name="game_states"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(
        GamePlayer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="game_wins",
    )
    objects = GameStateManager()

    def get_board(self, x: int, y: int) -> Board:
        return self.board_set.get(x=x, y=y)
