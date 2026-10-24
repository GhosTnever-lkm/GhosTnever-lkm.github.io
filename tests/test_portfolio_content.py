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
            "ModRelease Studio": "v0.3.90",
            "ModRelease Gate": "v1.0.72",
            "Paradox Mod Quality Gate": "v1.0.78",
            "Paradox Mod Workbench": "v0.2.14",
        }
        for card in cards[:4]:
            name = str(card["name"])
            links = card["links"]
            assert isinstance(links, list)
            release = next(link for link in links if link["text"].strip().startswith("Релиз v"))
            self.assertEqual(re.search(r"/releases/tag/(v[\d.]+)$", release["href"]).group(1), expected[name])
            self.assertIn(expected[name], release["text"])

        studio_links = cards[0]["links"]
        workbench = next(link for link in studio_links if "/paradox-mod-workbench/releases/tag/" in link["href"])
        self.assertEqual(workbench["href"], "https://github.com/GhosTnever-lkm/paradox-mod-workbench/releases/tag/v0.2.14")
        self.assertIn("Workbench v0.2.14", workbench["text"])

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

    def test_mod_observatory_release_and_download_links_are_current(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Mod Observatory")
        links = card["links"]
        release = next(link for link in links if "/mod-observatory/releases/tag/" in link["href"])
        archive = next(link for link in links if "/mod-observatory/releases/download/" in link["href"])
        self.assertEqual(release["href"], "https://github.com/GhosTnever-lkm/mod-observatory/releases/tag/v0.2.5")
        self.assertIn("v0.2.5", release["text"])
        self.assertEqual(archive["href"], "https://github.com/GhosTnever-lkm/mod-observatory/releases/download/v0.2.5/mod-observatory-0.2.5.zip")
        self.assertNotIn("v0.2.4", release["href"] + archive["href"])

    def test_game_text_gate_uses_its_published_release(self) -> None:
        html, cards = read_cards()
        game_text_cards = [card for card in cards if card["name"] == "GameText Gate"]
        self.assertEqual(len(game_text_cards), 2)
        self.assertEqual(html.count("game-text-gate/v0.1.17/docs/report-preview.png"), 2)
        self.assertNotIn("game-text-gate/v0.1.16/", html)
        for game_text in game_text_cards:
            links = game_text["links"]
            assert isinstance(links, list)
            release = next(link for link in links if link["text"].strip().startswith("Релиз v"))
            archive = next(link for link in links if "game-text-gate/releases/download/" in link["href"])
            self.assertEqual(release["href"], "https://github.com/GhosTnever-lkm/game-text-gate/releases/tag/v0.1.17")
            self.assertEqual(release["text"].strip(), "Релиз v0.1.17 ↗")
            self.assertEqual(archive["href"], "https://github.com/GhosTnever-lkm/game-text-gate/releases/download/v0.1.17/GameText-Gate-v0.1.17.zip")

    def test_mod_conflict_map_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Mod Conflict Map")
        links = card["links"]
        assert isinstance(links, list)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/tag/v0.4.4",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/download/v0.4.4/Mod-Conflict-Map-v0.4.4.zip",
            {link["href"] for link in links},
        )

    def test_asset_sieve_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Asset Sieve")
        links = card["links"]
        assert isinstance(links, list)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/asset-sieve/releases/tag/v0.1.6",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/asset-sieve/releases/download/v0.1.6/asset_sieve-0.1.6-py3-none-any.whl",
            {link["href"] for link in links},
        )

    def test_audioscribe_links_to_its_published_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "AudioScribe Studio")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/audioscribe-studio/releases/tag/v0.1.8", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/audioscribe-studio/releases/download/v0.1.8/AudioScribe-Studio-v0.1.8.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/audioscribe-studio/releases/download/v0.1.8/AudioScribe-Studio-v0.1.8.zip.sha256", hrefs)
        self.assertNotIn("v0.1.6", " ".join(hrefs))

    def test_json_compass_links_to_its_published_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "JSON Compass")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/json-compass/releases/tag/v1.0.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/json-compass/releases/download/v1.0.3/JSON-Compass-v1.0.3.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/json-compass/releases/download/v1.0.3/JSON-Compass-v1.0.3.zip.sha256", hrefs)
        self.assertFalse(any("json-compass/releases/tag/v1.0.2" in href for href in hrefs))

    def test_subtitle_timing_studio_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Subtitle Timing Studio")
        links = card["links"]
        assert isinstance(links, list)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/subtitle-timing-studio/releases/tag/v1.0.5",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/subtitle-timing-studio/releases/download/v1.0.5/Subtitle-Timing-Studio-1.0.5.zip",
            {link["href"] for link in links},
        )

    def test_captionbench_links_to_its_current_release_and_archive(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "CaptionBench")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/captionbench/releases/tag/v0.1.5", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/captionbench/releases/download/v0.1.5/CaptionBench-v0.1.5.zip", hrefs)
        self.assertFalse(any("captionbench/releases/tag/v0.1.2" in href for href in hrefs))

    def test_shiftledger_links_to_its_current_release_and_archive(self) -> None:
        html, cards = read_cards()
        card = next(card for card in cards if card["name"] == "ShiftLedger")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/shiftledger/releases/tag/v0.1.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/shiftledger/releases/download/v0.1.3/ShiftLedger-v0.1.3.zip", hrefs)
        self.assertFalse(any("shiftledger/releases/tag/v0.1.2" in href for href in hrefs))
        self.assertIn("20 МиБ", html)

    def test_tabharbor_links_to_its_current_release_assets(self) -> None:
        html, cards = read_cards()
        card = next(card for card in cards if card["name"] == "TabHarbor")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/tabharbor/releases/tag/v0.1.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/tabharbor/releases/download/v0.1.3/TabHarbor-v0.1.3.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/tabharbor/releases/download/v0.1.3/TabHarbor-v0.1.3.sha256", hrefs)
        self.assertFalse(any("tabharbor/releases/tag/v0.1.2" in href for href in hrefs))
        self.assertIn("100", html)

    def test_pixelclean_links_to_its_current_release_assets_and_preview(self) -> None:
        html, cards = read_cards()
        card = next(card for card in cards if card["name"] == "PixelClean Local")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/pixelclean-local/releases/tag/v0.1.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/pixelclean-local/releases/download/v0.1.3/pixelclean-local-v0.1.3.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/pixelclean-local/releases/download/v0.1.3/pixelclean-local-v0.1.3.zip.sha256", hrefs)
        start = html.index("<h3>PixelClean Local</h3>")
        end = html.index("</article>", start)
        card_html = html[start:end]
        self.assertIn("pixelclean-local/v0.1.3/docs/demo.svg", card_html)
        self.assertNotIn("v0.1.1", card_html)

    def test_commitcraft_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "CommitCraft")
        links = card["links"]
        assert isinstance(links, list)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/commitcraft/releases/tag/v1.0.5",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/commitcraft/archive/refs/tags/v1.0.5.zip",
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
