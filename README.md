# Little-Go Game (5x5) – AI Bots, GUI, and Tournament Simulator

This project implements a complete simulation and visualization framework for a simplified version of the board game Go — *Little-Go*, played on a 5x5 board. Developed as part of **CSCI 561: Foundations of AI**, the system allows you to test and visualize multiple AI strategies through a modern GUI and automated tournaments.

---

## 🧠 Project Features

- 🎨 **Modern Tkinter GUI** for visualizing gameplay between bots or humans.
- 🤖 **Multiple AI agents** including a custom Alpha-Beta bot developed by me.
- 🏁 `tournament.py` to run automated matches between any two bots for benchmarking.
- 📜 Adheres strictly to the Liberty, KO, and Komi rules as defined in the assignment.

---

## 🔍 My Custom Agent: `my_player.py`

- ✅ Developed and implemented by **Karan Sharad Owalekar**.
- ✅ Uses **Minimax with Alpha-Beta Pruning**
- ✅ Designed with custom functions to maximize territory and survival.
- 🥇 Consistently beat most bots in class tournaments during grading.

---

## 🤖 AI Players Overview

Each agent is a self-contained script inside the `players/` directory. All players read `input.txt` and write their move to `output.txt`.

| Player File              | Description                                                                                         |
|--------------------------|-----------------------------------------------------------------------------------------------------|
| `my_player.py`           | 🧠 Custom Alpha-Beta agent created by me. Uses strategic pruning and evaluation to win consistently.|
| `random_player.py`       | Places a stone randomly on any legal cell.                                                         |
| `greedy_player.py`       | Captures as many enemy stones as possible **in the current move only**.                            |
| `aggressive_player.py`   | Simulates **two-ply lookahead** to pick moves that lead to the most total enemy captures.          |
| `alphabeta_player.py`    | A Minimax-based player with Alpha-Beta Pruning (depth ≤ 2, branching ≤ 10), built by course staff. |

---

## 🖥 GUI: Play Bot vs Bot or Manual vs Bot

To launch the game with a beautiful board interface:

```bash
python main.py
```

```bash
python tournament.py -p1 player_1.py -p2 player_2.py -n 20
```

## 🎮 Gameplay Demo

Watch a quick video demonstration of the Little-Go GUI and AI agents in action:
![Image](https://github.com/user-attachments/assets/a10ca74e-db03-4bd0-b933-b32c62275d3a)
