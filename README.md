# GitChess

**English** | [한국어](README.ko.md)

*Play chess together through GitHub Issues.*

GitChess is a community chess project powered entirely by GitHub Issues and Actions. Install it in your own repository, and participants can submit moves through issue links. The bot validates each move and updates the chessboard in your README. No separate server or API key is required.

**Disabled by default.** The repository administrator must set `CHESS_ENABLED=true` before the chess workflow can run.

## Quick start

1. Choose **Use this template → Create a new repository** to create your own repository. You can also **Fork** this repository or copy the code. Any repository name works.
2. Enable **Settings → General → Features → Issues**.
3. Allow GitHub Actions under **Settings → Actions → General**. If you forked the repository, also enable workflows in the **Actions** tab. The chess workflow requests permission to write repository contents and issues using `GITHUB_TOKEN`.
4. Add a repository variable under **Settings → Secrets and variables → Actions → Variables**:

   | Name | Value |
   | :--- | :--- |
   | `CHESS_ENABLED` | `true` |

5. Open **Actions → GitChess → Run workflow**, select the default branch, and choose `new-game`.
6. Once the workflow finishes, refresh the README. The chessboard and move links will point to **your own repository**.

If you use branch protection rules, allow the bot to commit and push game updates. If your organization restricts write permissions, a repository administrator must allow the required permissions.

To stop the bot, delete the `CHESS_ENABLED` variable or set it to `false`. The chess job will be skipped for both new issues and manual runs.

## Chessboard

Current status: **<!-- BEGIN TURN -->not configured<!-- END TURN -->**

`white`: White to move · `black`: Black to move · `game over`: Game finished

<table>
<tr>
<td valign="top">

<!-- BEGIN CHESS BOARD -->
The chessboard will appear once you complete the quick start.
<!-- END CHESS BOARD -->

</td>
<td valign="top">

<!-- BEGIN MOVES LIST -->
Start a new game to generate the list of legal moves.
<!-- END MOVES LIST -->

</td>
</tr>
</table>

<!-- BEGIN GAME ACTIONS -->
For initial setup, use **Actions → GitChess → Run workflow → new-game**.
<!-- END GAME ACTIONS -->

## How to play

1. In the move list beside the board, choose a starting square (`FROM`) and a destination (`TO`).
2. Click the destination link and submit the issue without changing its title.
3. The bot posts the result and closes the issue. Refresh the README after the workflow finishes.

- Players are not assigned a color. Anyone can move a piece belonging to the side whose turn it is.
- The same user cannot play two consecutive turns.
- Only legal moves are allowed. Castling and en passant are supported; pawns are automatically promoted to queens.
- Anyone can start a new game after the current game ends. Only the repository owner can reset a game in progress.
- In a public repository, anyone who can open issues can participate. In a private repository, players need access to the repository.

To create an issue manually, use these titles:

```text
Chess: Move E2 to E4
Chess: Start new game
```

## Managing games

Select one of the following actions under **Actions → GitChess → Run workflow**:

| Action | Behavior |
| :--- | :--- |
| `new-game` | Reset the board and move history while keeping each participant's cumulative move count |
| `refresh` | Regenerate the board and issue links without changing the game. Use this after renaming your repository |

The distributed source does not include personal game data. Choose `new-game` when setting up a fresh installation.

## Local usage and development

You need Python 3.12 or later and [uv](https://docs.astral.sh/uv/). The script automatically installs its `chess` dependency when it runs.

```sh
# Start a new game: OWNER is the repository owner's GitHub username
uv run play.py seed OWNER OWNER/REPO

# Refresh the READMEs and board without changing the current game
uv run play.py refresh OWNER/REPO

# Play a move using the same logic as issue processing
uv run play.py play "Chess: Move E2 to E4" PLAYER OWNER OWNER/REPO

# Run tests
uv run --with chess python -m unittest discover -s tests -v
```

Local commands run explicitly regardless of `CHESS_ENABLED` and update the game state, READMEs, and SVG. Results are written as JSON to standard output and `/tmp/chess-result.json`.

## Project structure

| Path | Purpose |
| :--- | :--- |
| `play.py` | Process issue commands, validate chess moves, and generate READMEs and SVGs |
| `README.md` / `README.ko.md` | English and Korean documentation with synchronized chessboards |
| `data/game.json` | Board position (FEN), move history, and cumulative move counts, generated after setup |
| `board-*.svg` | Chessboard image, generated after setup |
| `.github/workflows/chess.yml` | Process issues and manual runs in enabled repositories |
| `tests/` | Regression tests for setup, gameplay, and rendering |

The chessboard, move list, turn, and new-game link are generated between the README's `BEGIN` / `END` comments. Keep these markers when editing either README. Both language versions are updated together.

Please use issues for bug reports and suggestions, and Pull Requests for code changes. Run the test command above to verify your changes.

## License

[MIT License](LICENSE)
