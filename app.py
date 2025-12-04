# app.py
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import random
import os
from jinja2 import DictLoader

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ---------------------------
# Templates as Python strings
# ---------------------------

base_html = """
<!doctype html>
<html lang="mn">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>5 Жижиг Тоглоомын Вебсайт</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background: linear-gradient(120deg,#f6f9ff,#eef7f9); min-height:100vh; }
      .card-game { border-radius: 18px; box-shadow: 0 8px 30px rgba(20,30,60,0.12); }
      .nav-game { gap:10px; flex-wrap:wrap; }
      .logo { font-weight:700; letter-spacing:0.4px; }
      .center-screen { display:flex; align-items:center; justify-content:center; min-height:60vh; padding:40px 0; }
      .maze { width:360px; height:360px; background:#fff; border-radius:12px; display:grid; grid-template-columns: repeat(12,1fr); grid-template-rows: repeat(12,1fr); gap:2px; padding:6px; }
      .cell { background:#e9f0ff; border-radius:4px; }
      .wall { background:#0b3b6f; }
      .player { background: linear-gradient(45deg,#ffddc2,#ff7a7a); display:flex; align-items:center; justify-content:center; font-weight:700; }
      .goal { background: linear-gradient(45deg,#c9ffd6,#6ee7b7); display:flex; align-items:center; justify-content:center; font-weight:700; }
    </style>
    {% block head %}{% endblock %}
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white py-3 shadow-sm">
      <div class="container">
        <a class="navbar-brand logo" href="{{ url_for('index') }}">MiniGames · Монгол</a>
        <div class="d-flex nav-game">
          <a class="btn btn-outline-primary btn-sm" href="{{ url_for('index') }}">Нүүр</a>
          <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('game', slug='guess') }}">1. Санасан тоог таах</a>
          <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('game', slug='rps') }}">2. Хайч/Чулуу/Даавуу</a>
          <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('game', slug='picture') }}">3. Зураг таах</a>
          <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('game', slug='fibo') }}">4. Фибоначчигийн таавар</a>
          <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('game', slug='maze') }}">5. Төөрдөг байшин</a>
        </div>
      </div>
    </nav>

    <div class="container my-5">
      {% block content %}{% endblock %}
    </div>

    <footer class="text-center py-4 text-muted">
      Made with ♥ — Run locally in VS Code (Flask)
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
  </body>
</html>
"""

index_html = """
{% extends "base.html" %}
{% block content %}
  <div class="row">
    <div class="col-md-8 mx-auto">
      <div class="card card-game p-4">
        <h3>5 Жижиг Тоглоом</h3>
        <p>Доорх тоглоомуудаас нэгийг сонгон, шууд браузер дээрээ тоглоно уу.</p>
        <div class="row g-3">
          <div class="col-md-6">
            <div class="p-3 border rounded">
              <h5>1. Санасан тоог таах</h5>
              <p>0-100 хоорон дахь санасан тоог би санаад байна. Та таалтаараа оруулна уу.</p>
              <a class="btn btn-primary" href="{{ url_for('game', slug='guess') }}">Тоглоход</a>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 border rounded">
              <h5>2. Хайч, Чулуу, Даавуу</h5>
              <p>Оюун ухаан ба аз сорих энгийн тоглоом.</p>
              <a class="btn btn-primary" href="{{ url_for('game', slug='rps') }}">Тоглоход</a>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 border rounded">
              <h5>3. Зураг таах</h5>
              <p>Зураг (emoji) харуулна — юу болохыг бичээрэй.</p>
              <a class="btn btn-primary" href="{{ url_for('game', slug='picture') }}">Тоглоход</a>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 border rounded">
              <h5>4. Фибоначчигийн таавар</h5>
              <p>Дараагийн тоог олоод оруулна уу.</p>
              <a class="btn btn-primary" href="{{ url_for('game', slug='fibo') }}">Тоглоход</a>
            </div>
          </div>
          <div class="col-12">
            <div class="p-3 border rounded">
              <h5>5. Төөрдөг байшин</h5>
              <p>Жижиг лабиринт — ←↑→↓ товчлуурууд ашиглан цэгийг гол руу хүргэнэ.</p>
              <a class="btn btn-primary" href="{{ url_for('game', slug='maze') }}">Тоглоход</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{% endblock %}
"""

# ---------------------------
# Helper game functions
# ---------------------------
def ensure_session():
    if 'games' not in session:
        session['games'] = {}

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    return render_template_string(index_html)

@app.route("/game/<slug>", methods=['GET','POST'])
def game(slug):
    ensure_session()
    # Dispatch to handlers
    if slug == 'guess':
        return guess_game()
    if slug == 'rps':
        return rps_game()
    if slug == 'picture':
        return picture_game()
    if slug == 'fibo':
        return fibo_game()
    if slug == 'maze':
        return maze_game()
    return redirect(url_for('index'))

# ---------------------------
# 1. Guess the Number
# ---------------------------
guess_html = """
{% extends "base.html" %}
{% block content %}
<div class="row center-screen">
  <div class="col-md-6">
    <div class="card p-4 card-game">
      <h4>1. Санасан тоог таах</h4>
      <p>0-100 хооронд нэг тоог би санаад байна. Та таалтаараа оруулна уу.</p>
      <form method="post">
        <div class="mb-2">
          <input class="form-control" type="number" name="guess" min="0" max="100" placeholder="Таасан тоо..." required>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-success" type="submit">Таах</button>
          <button class="btn btn-outline-secondary" name="action" value="reset">Ялсан/шинэ эхлэх</button>
        </div>
      </form>
      {% if message %}
        <div class="alert mt-3 alert-info">{{ message }}</div>
      {% endif %}
      <small class="text-muted">Оролт бүрт сервер таны таамагыг шалгана.</small>
    </div>
  </div>
</div>
{% endblock %}
"""

def guess_game():
    g = session['games'].get('guess')
    if not g or request.method == 'POST' and request.form.get('action') == 'reset':
        # init
        session['games']['guess'] = {'target': random.randint(0,100), 'tries':0}
        session.modified = True
        message = "Шинэ тоо таалагдсан. 0-100 хооронд таана уу!"
        return render_template_string(guess_html, message=message)
    if request.method == 'POST':
        guess_str = request.form.get('guess','')
        try:
            guess = int(guess_str)
        except:
            return render_template_string(guess_html, message="Зөв тоог оруулна уу.")
        g = session['games']['guess']
        g['tries'] += 1
        session.modified = True
        if guess == g['target']:
            message = f"Баяр хүргэе! Та {g['tries']} оролдлогоор зөв таав. Шинэ тоглоом эхлүүлэх 'Ялсан/шинэ эхлэх' дарна уу."
        elif guess < g['target']:
            message = "Их тоо байна (их)."
        else:
            message = "Бага тоо байна (бага)."
        return render_template_string(guess_html, message=message)
    # GET: ensure init
    if 'guess' not in session['games']:
        session['games']['guess'] = {'target': random.randint(0,100), 'tries':0}
        session.modified = True
    return render_template_string(guess_html, message=None)

# ---------------------------
# 2. Rock Paper Scissors
# ---------------------------
rps_html = """
{% extends "base.html" %}
{% block content %}
<div class="row center-screen">
  <div class="col-md-6">
    <div class="card p-4 card-game text-center">
      <h4>2. Хайч, Чулуу, Даавуу</h4>
      <p>Сонгоно уу:</p>
      <form method="post" class="d-flex justify-content-center gap-2">
        <button class="btn btn-outline-primary" name="choice" value="rock">Чулуу 🪨</button>
        <button class="btn btn-outline-primary" name="choice" value="paper">Даавуу 📄</button>
        <button class="btn btn-outline-primary" name="choice" value="scissors">Хайч ✂️</button>
      </form>
      {% if result %}
        <div class="mt-3">
          <p>Таны сонголт: <strong>{{ you }}</strong></p>
          <p>Сервер: <strong>{{ me }}</strong></p>
          <h5 class="mt-2">{{ result }}</h5>
        </div>
      {% endif %}
      <a class="btn btn-link mt-3" href="{{ url_for('game', slug='rps') }}">Дахин тоглох</a>
    </div>
  </div>
</div>
{% endblock %}
"""

def rps_game():
    if request.method == 'POST':
        you = request.form.get('choice')
        me = random.choice(['rock','paper','scissors'])
        outcomes = {
            ('rock','scissors'):'Та хожлоо! (Чулуу тасална)',
            ('scissors','paper'):'Та хожлоо! (Хайч зүснэ)',
            ('paper','rock'):'Та хожлоо! (Даавуу тойрог)',
        }
        if you == me:
            result = "Тэнцээ."
        elif (you, me) in outcomes:
            result = outcomes[(you,me)]
        else:
            # computer wins
            loses = {
                ('scissors','rock'):'Сервер хожлоо!',
                ('paper','scissors'):'Сервер хожлоо!',
                ('rock','paper'):'Сервер хожлоо!',
            }
            result = loses.get((you,me),'Үнэлж чадсангүй.')
        label = lambda k: {'rock':'Чулуу 🪨','paper':'Даавуу 📄','scissors':'Хайч ✂️'}.get(k,k)
        return render_template_string(rps_html, result=result, you=label(you), me=label(me))
    return render_template_string(rps_html, result=None)

# ---------------------------
# 3. Picture Guess (emoji)
# ---------------------------
picture_html = """
{% extends "base.html" %}
{% block content %}
<div class="row center-screen">
  <div class="col-md-6">
    <div class="card p-4 card-game">
      <h4>3. Зураг таах</h4>
      <p>Доорх дүрс (emoji)-г харж юу болохыг бичнэ үү.</p>
      <div class="fs-1 text-center mb-3">{{ emoji }}</div>
      <form method="post">
        <input class="form-control mb-2" name="answer" placeholder="Юу байна вэ? (монгол/англи богино бич...)">
        <div class="d-flex gap-2">
          <button class="btn btn-success" type="submit">Шалгах</button>
          <button class="btn btn-outline-secondary" name="action" value="new">Шинэ</button>
        </div>
      </form>
      {% if msg %}
        <div class="alert mt-3 {{'alert-success' if ok else 'alert-danger'}}">{{ msg }}</div>
      {% endif %}
      <small class="text-muted">Жишээ: "хоёр дугуй" эсвэл "bicycle".</small>
    </div>
  </div>
</div>
{% endblock %}
"""

PICTURES = [
    ("🚲", ["bicycle","дугуй","bicycle"]),
    ("🍎", ["apple","алим"]),
    ("🐶", ["dog","нохой"]),
    ("✈️", ["plane","онгоц"]),
    ("🎸", ["guitar","гитар"]),
    ("🌵", ["cactus","кактус"]),
]

def picture_game():
    if 'picture' not in session['games'] or (request.method == 'POST' and request.form.get('action') == 'new'):
        session['games']['picture'] = {'idx': random.randrange(len(PICTURES))}
        session.modified = True
    idx = session['games']['picture']['idx']
    emoji, answers = PICTURES[idx]
    msg = None
    ok = False
    if request.method == 'POST' and request.form.get('action') != 'new':
        guess = (request.form.get('answer') or "").strip().lower()
        if any(guess == a for a in answers):
            msg = "Зөв! Та зөв таалаа."
            ok = True
        else:
            msg = f"Буруу. Зөв хариултуудын жишээ: {', '.join(answers[:2])}"
    return render_template_string(picture_html, emoji=emoji, msg=msg, ok=ok)

# ---------------------------
# 4. Fibonacci next number
# ---------------------------
fibo_html = """
{% extends "base.html" %}
{% block content %}
<div class="row center-screen">
  <div class="col-md-6">
    <div class="card p-4 card-game">
      <h4>4. Фибоначчигийн таавар</h4>
      <p>Дараах дарааллын дараагийн тоог олоно уу:</p>
      <div class="fs-4 my-2"> {{ seq_display }} , ... </div>
      <form method="post">
        <input class="form-control mb-2" name="next" placeholder="Дараагийн тоо">
        <div class="d-flex gap-2">
          <button class="btn btn-success" type="submit">Шалгах</button>
          <button class="btn btn-outline-secondary" name="action" value="next">Дараагийн дасгал</button>
        </div>
      </form>
      {% if msg %}
        <div class="alert mt-3 {{'alert-success' if ok else 'alert-danger'}}">{{ msg }}</div>
      {% endif %}
    </div>
  </div>
</div>
{% endblock %}
"""

def fibo_seq(n):
    a,b = 0,1
    seq=[]
    for _ in range(n):
        seq.append(a)
        a,b = b,a+b
    return seq

def fibo_game():
    if 'fibo' not in session['games'] or (request.method == 'POST' and request.form.get('action') == 'next'):
        # choose random length 5..7 and offset
        n = random.randint(5,7)
        seq = fibo_seq(n+1)  # we keep n+1 so last is the answer
        # maybe slice to show last n terms
        session['games']['fibo'] = {'full': seq, 'show': n}
        session.modified = True
    info = session['games']['fibo']
    seq = info['full']
    show = info['show']
    display = ", ".join(str(x) for x in seq[:show])
    msg=None; ok=False
    if request.method == 'POST' and request.form.get('action') != 'next':
        try:
            nxt = int(request.form.get('next',''))
            correct = seq[show]
            if nxt == correct:
                msg = f"Зөв! Дараагийн тоо {correct}."
                ok = True
            else:
                msg = f"Буруу. Зөв хариулт {correct}."
        except:
            msg = "Тоо оруулна уу."
    return render_template_string(fibo_html, seq_display=display, msg=msg, ok=ok)

# ---------------------------
# 5. Maze (client-side)
# ---------------------------
maze_html = """
{% extends "base.html" %}
{% block content %}
<div class="row center-screen">
  <div class="col-md-8">
    <div class="card p-4 card-game">
      <h4>5. Төөрдөг байшин (лавиринт)</h4>
      <p>Товчлуурууд: ← ↑ → ↓ эсвэл WASD ашиглан "P" үсгийг (тоглогч) гол (G) руу зөөх.</p>

      <div class="d-flex justify-content-center my-3">
        <div id="maze" class="maze"></div>
      </div>

      <div class="text-center">
        <button id="resetBtn" class="btn btn-outline-secondary">Сэргээх</button>
        <span class="mx-3" id="status"></span>
      </div>
      <small class="text-muted d-block mt-2">Жишээ сахилга: сахилга бат шаарддаг — амжилт!</small>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
const rows = 12, cols = 12;
const mazeEl = document.getElementById('maze');
const statusEl = document.getElementById('status');
let grid = [];
let player = {r:1,c:1};
let goal = {r:10,c:10};

function buildRandomMaze(){
  grid = [];
  mazeEl.innerHTML = '';
  for(let r=0;r<rows;r++){
    for(let c=0;c<cols;c++){
      const cell = document.createElement('div');
      cell.classList.add('cell');
      // border wall edges
      if(r===0||c===0||r===rows-1||c===cols-1) {
        cell.classList.add('wall');
      } else {
        // random walls but keep start and goal clear
        if(Math.random() < 0.18 && !(r===1&&c===1) && !(r===goal.r&&c===goal.c)) {
          cell.classList.add('wall');
        }
      }
      cell.id = `cell-${r}-${c}`;
      mazeEl.appendChild(cell);
    }
  }
  placePlayer();
  placeGoal();
}

function placePlayer(){
  // find free spot near (1,1)
  player = {r:1,c:1};
  const el = document.getElementById(`cell-${player.r}-${player.c}`);
  el.classList.remove('wall'); el.classList.add('player'); el.textContent='P';
}

function placeGoal(){
  const el = document.getElementById(`cell-${goal.r}-${goal.c}`);
  el.classList.remove('wall'); el.classList.add('goal'); el.textContent='G';
}

function move(dr,dc){
  const nr = player.r + dr;
  const nc = player.c + dc;
  const target = document.getElementById(`cell-${nr}-${nc}`);
  if(!target) return;
  if(target.classList.contains('wall')) return;
  // move
  const old = document.getElementById(`cell-${player.r}-${player.c}`);
  old.classList.remove('player'); old.textContent='';
  player.r = nr; player.c = nc;
  const cur = document.getElementById(`cell-${player.r}-${player.c}`);
  cur.classList.add('player'); cur.textContent='P';
  checkGoal();
}

function checkGoal(){
  if(player.r === goal.r && player.c === goal.c){
    statusEl.textContent = "Баяр хүргэе! Та зорилгодоо хүрлээ 🎉";
  } else {
    statusEl.textContent = "";
  }
}

document.addEventListener('keydown',(e)=>{
  const key = e.key;
  if(['ArrowUp','w','W'].includes(key)) move(-1,0);
  if(['ArrowDown','s','S'].includes(key)) move(1,0);
  if(['ArrowLeft','a','A'].includes(key)) move(0,-1);
  if(['ArrowRight','d','D'].includes(key)) move(0,1);
});

document.getElementById('resetBtn').addEventListener('click', ()=>{
  buildRandomMaze();
  statusEl.textContent = "";
});

// init
buildRandomMaze();
</script>
{% endblock %}
"""

def maze_game():
    return render_template_string(maze_html)

# ---------------------------
# Make base.html available via DictLoader (Flask 3 compatible)
# ---------------------------
app.jinja_loader = DictLoader({'base.html': base_html})

# Optional context processor (keeps available names)
@app.context_processor
def inject_base():
    return dict()

# ---------------------------
# Run server
# ---------------------------
if __name__ == "__main__":
    # By default Flask uses port 5000. If you need a different port, change here:
    app.run(debug=True)
