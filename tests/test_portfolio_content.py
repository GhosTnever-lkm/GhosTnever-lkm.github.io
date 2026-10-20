from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PortfolioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[dict[str, object]] = []
        self.card: dict[str, object] | None = None
        self.in_heading = False
        self.link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "article" and "project-card" in (values.get("class") or "").split():
            self.card = {"name": "", "links": []}
        elif self.card is not None and tag == "h3":
            self.in_heading = True
        elif self.card is not None and tag == "a":
            self.link = {"href": values.get("href") or "", "text": ""}

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3":
            self.in_heading = False
        elif tag == "a" and self.link is not None and self.card is not None:
            links = self.card["links"]
            assert isinstance(links, list)
            links.append(self.link)
            self.link = None
        elif tag == "article" and self.card is not None:
            self.cards.append(self.card)
            self.card = None

    def handle_data(self, data: str) -> None:
        if self.card is not None and self.in_heading:
            self.card["name"] = str(self.card["name"]) + data
        if self.link is not None:
            self.link["text"] += data


def read_cards() -> tuple[str, list[dict[str, object]]]:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = PortfolioParser()
    parser.feed(html)
    return html, parser.cards


class PortfolioContentTests(unittest.TestCase):
    def test_featured_mod_release_ecosystem_is_current_and_ordered(self) -> None:
        _, cards = read_cards()
        self.assertEqual(
            [card["name"] for card in cards[:4]],
            [
                "ModRelease Studio",
                "ModRelease Gate",
                "Paradox Mod Quality Gate",
                "Paradox Mod Workbench",
            ],
        )
        expected = {
            "ModRelease Studio": "v0.3.88",
            "ModRelease Gate": "v1.0.70",
            "Paradox Mod Quality Gate": "v1.0.73",
            "Paradox Mod Workbench": "v0.2.8",
        }
        for card in cards[:4]:
            name = str(card["name"])
            links = card["links"]
            assert isinstance(links, list)
            release = next(link for link in links if link["text"].strip().startswith("Релиз v"))
            self.assertEqual(re.search(r"/releases/tag/(v[\d.]+)$", release["href"]).group(1), expected[name])
            self.assertIn(expected[name], release["text"])

    def test_every_workflow_link_points_to_its_own_project(self) -> None:
        _, cards = read_cards()
        for card in cards:
            links = card["links"]
            assert isinstance(links, list)
            workflows = [link for link in links if "/actions/workflows/" in link["href"]]
            if not workflows:
                continue
            source = next(link for link in links if link["text"].strip() == "Исходный код ↗")
            source_repo = source["href"].rstrip("/")
            for workflow in workflows:
                self.assertTrue(
                    workflow["href"].startswith(source_repo + "/actions/workflows/"),
                    f"{card['name']} links its CI badge to a different repository: {workflow['href']}",
                )

    def test_game_text_gate_uses_its_published_release(self) -> None:
        _, cards = read_cards()
        game_text = next(card for card in cards if card["name"] == "GameText Gate")
        links = game_text["links"]
        assert isinstance(links, list)
        release = next(link for link in links if link["text"].strip().startswith("Релиз v"))
        self.assertEqual(release["href"], "https://github.com/GhosTnever-lkm/game-text-gate/releases/tag/v0.1.16")
        self.assertEqual(release["text"].strip(), "Релиз v0.1.16 ↗")

    def test_mod_conflict_map_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Mod Conflict Map")
        links = card["links"]
        assert isinstance(links, list)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/tag/v0.4.2",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/download/v0.4.2/Mod-Conflict-Map-v0.4.2.zip",
            {link["href"] for link in links},
        )

    def test_pages_workflow_checks_pull_requests_without_deploying_them(self) -> None:
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertRegex(workflow, r"(?m)^  pull_request:")
        self.assertRegex(workflow, r"(?m)^  validate:")
        self.assertRegex(workflow, r"(?m)^    needs: validate$")
        self.assertRegex(
            workflow,
            r"(?m)^    if: github\.event_name != 'pull_request' && github\.ref == 'refs/heads/main'$")


if __name__ == "__main__":
    unittest.main()
