# Ludo Game (Flask + HTML/CSS/JS)

This is a simple Ludo prototype with a Flask backend and a minimal HTML/CSS/JS UI. It demonstrates turns, dice rolls, simple piece movement (enter on 6, move along a 52-position loop, finish on exact count), and reset.

## Requirements

- Python 3.9+
- pip

## Setup

```bash
pip install flask
```

## Run

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

## Notes

- The board UI is a simplified 13x13 grid; pieces travel around the perimeter to represent 52 positions. It is not a pixel-perfect Ludo board, but good enough to play turns.
- Rules implemented are minimal: need 6 to enter; exact roll to finish; rolling a 6 grants another turn.
- You can reset the game using the Reset button.