import json

from flask import Flask, redirect, render_template_string, url_for

from board import board
from randomplayer import randomplayer
from agent import agent

learner = agent(epsilon=0)
learner.load("q_table.json")

app = Flask(__name__)
game_board = board()
result = None
computer_starts = False
opponent_type = "random"
inverted_colors = False

GAME_PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tic-Tac-Toe Party</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body class="{% if inverted_colors %}inverted{% endif %}">
    <svg width="0" height="0" style="position:absolute" aria-hidden="true">
        <defs>
            {% for id, seed in [('wood-x', 3), ('wood-o', 17)] %}
            <filter id="{{ id }}" filterUnits="userSpaceOnUse" x="0" y="0" width="100" height="100" color-interpolation-filters="sRGB">
                <!-- grain, tinted with the piece colour -->
                <feTurbulence type="fractalNoise" baseFrequency="0.018 0.32" numOctaves="5" seed="{{ seed }}" result="noise"/>
                <feColorMatrix in="noise" type="matrix" result="grain"
                    values="0 0 0 0.9 0.3  0 0 0 0.9 0.3  0 0 0 0.9 0.3  0 0 0 0 1"/>
                <feFlood class="tint" result="tint"/>
                <feComposite in="grain" in2="tint" operator="arithmetic" k1="1" result="wood"/>
                <!-- rounded bevel from the shape's alpha -->
                <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="bump"/>
                <feDiffuseLighting in="bump" surfaceScale="6" diffuseConstant="1.3" lighting-color="#fff" result="shade">
                    <feDistantLight azimuth="235" elevation="50"/>
                </feDiffuseLighting>
                <feSpecularLighting in="bump" surfaceScale="6" specularConstant="0.8" specularExponent="25" lighting-color="#fff6e6" result="spec">
                    <feDistantLight azimuth="235" elevation="50"/>
                </feSpecularLighting>
                <feComposite in="wood" in2="shade" operator="arithmetic" k1="1" result="lit"/>
                <feComposite in="lit" in2="spec" operator="arithmetic" k2="1" k3="0.55" result="glossy"/>
                <feComposite in="glossy" in2="SourceAlpha" operator="in" result="piece"/>
                <!-- contact shadow on the square -->
                <feGaussianBlur in="SourceAlpha" stdDeviation="2.5" result="sblur"/>
                <feOffset in="sblur" dx="2" dy="4" result="soff"/>
                <feColorMatrix in="soff" type="matrix" result="shadow"
                    values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.65 0"/>
                <feMerge><feMergeNode in="shadow"/><feMergeNode in="piece"/></feMerge>
            </filter>
            {% endfor %}
        </defs>
    </svg>
    <main>
        <span class="eyebrow">A tiny game, big drama</span>
        <h1>Tic-Tac-Toe</h1>
        <p class="subtitle">Three in a row wins. Gloating is optional.</p>
        <p class="message" role="status">{{ message }}</p>
        <form class="board" aria-label="Tic-Tac-Toe board">
            {% for cell in cells %}
            <button class="cell{% if cell == 'X' %} x{% elif cell == 'O' %} o{% endif %}"
                    type="submit" formaction="{{ url_for('move', cell=loop.index0) }}"
                    formmethod="post"
                    aria-label="Cell {{ loop.index }}{% if cell != '.' %}: {{ cell }}{% endif %}"
                    {% if cell != '.' or result %}disabled{% endif %}>{% if cell == 'X' %}<svg class="piece" viewBox="0 0 100 100" aria-hidden="true"><path d="M27 27L73 73M73 27L27 73" stroke="#000" stroke-width="17" stroke-linecap="round" filter="url(#wood-x)"/></svg>{% elif cell == 'O' %}<svg class="piece" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="24" fill="none" stroke="#000" stroke-width="15" filter="url(#wood-o)"/></svg>{% endif %}</button>
            {% endfor %}
        </form>
        <section class="controls" aria-label="Game settings">
            <p class="controls-title">Make it your game</p>
            <div class="control-row">
                <form class="control-form" action="{{ url_for('toggle_start') }}" method="post">
                    <button class="control-button" type="submit">
                        {% if computer_starts %}🤖 Computer starts{% else %}🙋 You start{% endif %}
                    </button>
                </form>
                <form class="control-form" action="{{ url_for('toggle_opponent') }}" method="post">
                    <button class="control-button" type="submit">
                        {% if opponent_type == 'learner' %}🧠 The learner{% else %}🎲 Random opponent{% endif %}
                    </button>
                </form>
                <form class="control-form" action="{{ url_for('toggle_colors') }}" method="post">
                    <button class="control-button" type="submit">
                        {% if inverted_colors %}🌲 Dark oak{% else %}🪵 Birch{% endif %}
                    </button>
                </form>
                <a class="control-button" href="{{ url_for('battle_log') }}">📜 AI battle log</a>
            </div>
            <form action="{{ url_for('reset') }}" method="post">
                <button class="new-game" type="submit">↻ New game</button>
            </form>
        </section>
    </main>
</body>
</html>
"""


def start_new_game():
    global result

    game_board.restart()
    result = None
    if computer_starts:
        computer_move()


def computer_move():
    if opponent_type == "learner":
        # The agent was trained as X, so swap marks: computer (O) -> X, human (X) -> O.
        state = game_board.to_key().translate(str.maketrans("XO", "OX"))
        if "." in state:
            game_board.make_move(divmod(learner.best_action(state), 3), "O")
    else:
        randomplayer("O").choose_move(game_board)


@app.route("/")
def home():
    if result == "X":
        message = "You win! Somebody call the press! 🎉"
    elif result == "O":
        message = "The computer wins this round. Rematch? 🤖"
    elif result == "draw":
        message = "It's a draw! The board lives to see another day. 🤝"
    elif computer_starts and not any(cell != "." for cell in game_board.to_key()):
        message = "The computer is ready. Your turn! 👀"
    elif computer_starts and game_board.to_key().count("O") == 1 and game_board.to_key().count("X") == 0:
        message = "The computer made the first move. Your turn! 👀"
    else:
        message = "Your turn — you're X. Make your mark! ✨"

    return render_template_string(
        GAME_PAGE,
        cells=game_board.to_key(),
        result=result,
        message=message,
        computer_starts=computer_starts,
        opponent_type=opponent_type,
        inverted_colors=inverted_colors,
    )


@app.route("/move/<int:cell>", methods=["POST"])
def move(cell):
    global result

    if result is not None or cell not in range(9):
        return redirect(url_for("home"))

    if not game_board.make_move(divmod(cell, 3), "X"):
        return redirect(url_for("home"))

    if game_board.winner() == "X":
        result = "X"
    elif game_board.is_full():
        result = "draw"
    else:
        computer_move()
        if game_board.winner() == "O":
            result = "O"
        elif game_board.is_full():
            result = "draw"

    return redirect(url_for("home"))


@app.route("/reset", methods=["POST"])
def reset():
    start_new_game()
    return redirect(url_for("home"))


@app.route("/toggle-start", methods=["POST"])
def toggle_start():
    global computer_starts

    computer_starts = not computer_starts
    start_new_game()
    return redirect(url_for("home"))


@app.route("/toggle-opponent", methods=["POST"])
def toggle_opponent():
    global opponent_type

    opponent_type = "learner" if opponent_type == "random" else "random"
    start_new_game()
    return redirect(url_for("home"))


@app.route("/toggle-colors", methods=["POST"])
def toggle_colors():
    global inverted_colors

    inverted_colors = not inverted_colors
    return redirect(url_for("home"))


LOG_PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Battle Log</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body class="{% if inverted_colors %}inverted{% endif %}">
    <main class="wide">
        <span class="eyebrow">Training archive</span>
        <h1>AI Battle Log</h1>
        {% if not blocks %}
        <p class="message">No training log yet. Run <code>python game.py</code> first.</p>
        {% else %}
        <p class="subtitle">{{ "{:,}".format(meta.episodes) }} games against a random opponent ·
            α {{ meta.alpha }} · γ {{ meta.gamma }} · draw reward {{ meta.rewards.draw }}</p>
        <div class="stats">
            <div class="stat"><small>First block win</small><b>{{ first_win }}%</b></div>
            <div class="stat"><small>Last block win</small><b>{{ last_win }}%</b></div>
            <div class="stat"><small>First block loss</small><b>{{ first_loss }}%</b></div>
            <div class="stat"><small>Last block loss</small><b>{{ last_loss }}%</b></div>
        </div>
        <h2>Results per {{ "{:,}".format(block_size) }} games</h2>
        <div class="legend">
            <span><i style="background:#2e8b57"></i>Wins</span>
            <span><i style="background:#c0392b"></i>Losses</span>
            <span><i style="background:#8a7a5a"></i>Draws</span>
        </div>
        <svg class="chart" viewBox="0 0 {{ W }} {{ H }}" role="img" aria-label="Win, loss and draw percentage over training">
            {% for pct in [0, 25, 50, 75, 100] %}
            {% set y = PAD + (H - 2*PAD) * (1 - pct/100) %}
            <line x1="{{ PAD }}" x2="{{ W - PAD/2 }}" y1="{{ y }}" y2="{{ y }}" stroke="#0000001a"/>
            <text x="{{ PAD - 6 }}" y="{{ y + 4 }}" font-size="11" text-anchor="end" fill="#6b6156">{{ pct }}%</text>
            {% endfor %}
            <polyline points="{{ lines.wins }}" fill="none" stroke="#2e8b57" stroke-width="2.5" stroke-linejoin="round"/>
            <polyline points="{{ lines.losses }}" fill="none" stroke="#c0392b" stroke-width="2.5" stroke-linejoin="round"/>
            <polyline points="{{ lines.draws }}" fill="none" stroke="#8a7a5a" stroke-width="2" stroke-linejoin="round"/>
            <text x="{{ PAD }}" y="{{ H - 8 }}" font-size="11" fill="#6b6156">episode 1</text>
            <text x="{{ W - PAD/2 }}" y="{{ H - 8 }}" font-size="11" text-anchor="end" fill="#6b6156">{{ "{:,}".format(meta.episodes) }}</text>
        </svg>
        <h2>Battle records</h2>
        <div class="table-wrap">
            <table class="log-table">
                <thead><tr><th>Episodes</th><th>Wins</th><th>Losses</th><th>Draws</th><th>Win %</th><th>ε</th></tr></thead>
                <tbody>
                {% for b in blocks %}
                <tr><td>{{ b.start }}–{{ b.end }}</td><td>{{ b.wins }}</td><td>{{ b.losses }}</td><td>{{ b.draws }}</td>
                    <td>{{ "%.1f"|format(100 * b.wins / block_size) }}</td><td>{{ "%.2f"|format(b.epsilon) }}</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        <a class="new-game" href="{{ url_for('home') }}">← Back to the game</a>
    </main>
</body>
</html>
"""


@app.route("/battle-log")
def battle_log():
    try:
        with open("training_log.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"meta": {}, "blocks": []}
    blocks = data["blocks"]
    W, H, PAD = 800, 300, 40
    ctx = dict(blocks=blocks, meta=data["meta"], W=W, H=H, PAD=PAD, inverted_colors=inverted_colors)
    if blocks:
        size = blocks[0]["end"] - blocks[0]["start"] + 1
        step = (W - 1.5 * PAD) / max(len(blocks) - 1, 1)

        def line(key):
            return " ".join(
                f"{PAD + i * step:.1f},{PAD + (H - 2 * PAD) * (1 - b[key] / size):.1f}"
                for i, b in enumerate(blocks)
            )

        pct = lambda b, k: round(100 * b[k] / size, 1)
        ctx.update(
            block_size=size,
            lines={k: line(k) for k in ("wins", "losses", "draws")},
            first_win=pct(blocks[0], "wins"), last_win=pct(blocks[-1], "wins"),
            first_loss=pct(blocks[0], "losses"), last_loss=pct(blocks[-1], "losses"),
        )
    return render_template_string(LOG_PAGE, **ctx)


if __name__ == "__main__":
    app.run(debug=True)
