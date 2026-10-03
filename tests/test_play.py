import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import chess

import play


class ProjectTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.readme = self.root / "README.md"
        self.readme.write_text(play.README_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        self.korean_readme = self.root / "README.ko.md"
        self.korean_readme.write_text(
            (play.ROOT / "README.ko.md").read_text(encoding="utf-8"), encoding="utf-8"
        )
        for name, value in (
            ("ROOT", self.root),
            ("GAME_PATH", self.root / "data" / "game.json"),
            ("README_PATH", self.readme),
        ):
            patcher = patch.object(play, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_command(self, *arguments):
        with patch.object(sys, "argv", ["play.py", *arguments]):
            return play._run()

    def start_game(self):
        return self.run_command("seed", "owner", "owner/issue-chess")

    def move(self, title, author):
        return self.run_command("play", title, author, "owner", "owner/issue-chess")

    def test_fresh_install_creates_game_and_repository_specific_readme(self):
        self.assertFalse(play.GAME_PATH.exists())

        result = self.start_game()

        self.assertTrue(result["ok"])
        game = play.load()
        self.assertEqual(game.fen, chess.Board().fen())
        self.assertEqual(game.history, (("start", "owner", ""),))
        self.assertEqual(game.scores, ())
        self.assertFalse(game.finished)
        readme = self.readme.read_text(encoding="utf-8")
        self.assertIn("https://github.com/owner/issue-chess/issues/new", readme)
        self.assertIn("<!-- BEGIN TURN -->white<!-- END TURN -->", readme)
        self.assertNotIn("<!-- BEGIN TURN -->not configured<!-- END TURN -->", readme)
        self.assertIn("[Start a new game](https://github.com/owner/issue-chess/", readme)
        self.assertEqual(len(list(self.root.glob("board-*.svg"))), 1)

    def test_refresh_preserves_game_and_updates_all_issue_links(self):
        self.start_game()
        self.move("Chess: Move E2 to E4", "alice")
        self.move("Chess: Move E7 to E5", "bob")
        original_state = play.GAME_PATH.read_bytes()

        result = self.run_command("refresh", "another-owner/renamed-chess")

        self.assertTrue(result["ok"])
        self.assertEqual(play.GAME_PATH.read_bytes(), original_state)
        readme = self.readme.read_text(encoding="utf-8")
        self.assertIn("https://github.com/another-owner/renamed-chess/issues/new", readme)
        self.assertNotIn("https://github.com/owner/issue-chess/issues/new", readme)
        self.assertNotIn("https://github.com/jeonjw85/jeonjw85/issues/new", readme)
        self.assertIn("[Start a new game](https://github.com/another-owner/renamed-chess/", readme)
        self.assertIn("<!-- BEGIN TURN -->white<!-- END TURN -->", readme)
        self.assertIn("# GitChess", readme)
        boards = list(self.root.glob("board-*.svg"))
        self.assertEqual(len(boards), 1)
        self.assertIn(boards[0].name, readme)
        self.assertIn("<svg", boards[0].read_text(encoding="utf-8"))

    def test_both_readmes_update_with_localized_links(self):
        self.start_game()
        self.move("Chess: Move E2 to E4", "alice")
        self.run_command("refresh", "another-owner/gitchess")

        english = self.readme.read_text(encoding="utf-8")
        korean = self.korean_readme.read_text(encoding="utf-8")
        self.assertIn("[Start a new game]", english)
        self.assertNotIn("[새 게임 시작]", english)
        self.assertIn("[새 게임 시작]", korean)
        self.assertIn("[한국어](README.ko.md)", english)
        self.assertIn("[English](README.md)", korean)
        board_path = next(self.root.glob("board-*.svg"))
        for readme in (english, korean):
            self.assertIn("<!-- BEGIN TURN -->black<!-- END TURN -->", readme)
            self.assertIn("https://github.com/another-owner/gitchess/issues/new", readme)
            self.assertNotIn("https://github.com/owner/issue-chess/issues/new", readme)
            self.assertIn(board_path.name, readme)

    def test_english_readme_can_run_without_korean_translation(self):
        self.korean_readme.unlink()

        self.assertTrue(self.start_game()["ok"])
        self.assertIn("[Start a new game]", self.readme.read_text(encoding="utf-8"))

    def test_refresh_without_game_leaves_readme_untouched(self):
        original_readme = self.readme.read_bytes()

        result = self.run_command("refresh", "owner/issue-chess")

        self.assertFalse(result["ok"])
        self.assertFalse(play.GAME_PATH.exists())
        self.assertEqual(self.readme.read_bytes(), original_readme)

    def test_legal_move_updates_board_history_and_score(self):
        self.start_game()

        result = self.move("Chess: Move E2 to E4", "alice")

        self.assertTrue(result["ok"])
        self.assertIn("repository README", result["comment"])
        game = play.load()
        self.assertEqual(game.history[0], ("move", "alice", "e2e4"))
        self.assertEqual(dict(game.scores), {"alice": 1})
        board = chess.Board()
        board.push_uci("e2e4")
        self.assertEqual(game.fen, board.fen())
        self.assertIn("<!-- BEGIN TURN -->black<!-- END TURN -->", self.readme.read_text())

    def test_rejected_moves_do_not_change_state(self):
        self.start_game()
        self.move("Chess: Move E2 to E4", "alice")
        original_state = play.GAME_PATH.read_bytes()
        original_readme = self.readme.read_bytes()

        for title, author in (
            ("Chess: Move E7 to E5", "alice"),
            ("Chess: Move E7 to E4", "bob"),
        ):
            with self.subTest(title=title, author=author):
                self.assertFalse(self.move(title, author)["ok"])
                self.assertEqual(play.GAME_PATH.read_bytes(), original_state)
                self.assertEqual(self.readme.read_bytes(), original_readme)

    def test_only_owner_can_reset_active_game_and_scores_are_kept(self):
        self.start_game()
        self.move("Chess: Move E2 to E4", "alice")
        original_state = play.GAME_PATH.read_bytes()

        self.assertFalse(self.move("Chess: Start new game", "alice")["ok"])
        self.assertEqual(play.GAME_PATH.read_bytes(), original_state)
        self.assertTrue(self.move("Chess: Start new game", "owner")["ok"])
        game = play.load()
        self.assertEqual(game.fen, chess.Board().fen())
        self.assertEqual(game.history, (("start", "owner", ""),))
        self.assertEqual(dict(game.scores), {"alice": 1})

    def test_finished_game_can_be_restarted_by_participant(self):
        self.start_game()
        for title, author in (
            ("Chess: Move F2 to F3", "alice"),
            ("Chess: Move E7 to E5", "bob"),
            ("Chess: Move G2 to G4", "alice"),
            ("Chess: Move D8 to H4", "bob"),
        ):
            self.assertTrue(self.move(title, author)["ok"])

        self.assertTrue(play.load().finished)
        self.assertIn("<!-- BEGIN TURN -->game over<!-- END TURN -->", self.readme.read_text())
        self.assertTrue(self.move("Chess: Start new game", "alice")["ok"])
        self.assertFalse(play.load().finished)
        self.assertEqual(dict(play.load().scores), {"alice": 2, "bob": 2})


if __name__ == "__main__":
    unittest.main()
