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
    def test_version_and_changelog_record_current_portfolio_release(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertEqual(version, "1.3.274")
        self.assertTrue(changelog.startswith("## 1.3.274 - 2026-10-25"))
        self.assertIn("ShaderTriage", changelog)
        self.assertIn("VOIDFALL", changelog)
        self.assertIn("ContrastKit", changelog)
        self.assertIn("BugBundle", changelog)
        self.assertIn("Subtitle Timing Studio", changelog)
        html, _ = read_cards()
        self.assertIn("https://raw.githubusercontent.com/GhosTnever-lkm/bugbundle/v1.0.12/docs/bugbundle-preview.png", html)
        self.assertIn("https://github.com/GhosTnever-lkm/bugbundle/releases/download/v1.0.12/BugBundle-v1.0.12.zip", html)

    def test_homeledger_links_to_current_v015_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "HomeLedger")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/homeledger/releases/tag/v0.1.5", hrefs)
        self.assertTrue(any("Релиз v0.1.5" in link["text"] for link in links))
        self.assertIn(
            "https://github.com/GhosTnever-lkm/homeledger/releases/download/v0.1.5/HomeLedger-v0.1.5.zip",
            hrefs,
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/homeledger/releases/download/v0.1.5/HomeLedger-v0.1.5.sha256",
            hrefs,
        )
        self.assertFalse(any("homeledger/releases/" in href and "v0.1.4" in href for href in hrefs))

    def test_workshop_page_studio_links_to_verified_app_and_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Workshop Page Studio")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://ghostnever-lkm.github.io/workshop-page-studio/", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/workshop-page-studio", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/workshop-page-studio/releases/tag/v0.2.2", hrefs)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/workshop-page-studio/releases/download/v0.2.2/Workshop-Page-Studio-v0.2.2.zip",
            hrefs,
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/workshop-page-studio/releases/download/v0.2.2/Workshop-Page-Studio-v0.2.2-SHA256SUMS.txt",
            hrefs,
        )

    def test_frameforge_links_to_current_release_archive_and_checksum(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "FrameForge")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/frameforge/releases/tag/v1.18.2", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/frameforge/releases/download/v1.18.2/FrameForge-1.18.2-windows-x64.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/frameforge/releases/download/v1.18.2/FrameForge-1.18.2-windows-x64.zip.sha256", hrefs)
        self.assertFalse(any("frameforge/releases/tag/v1.18.1" in href for href in hrefs))

    def test_regexbench_card_links_to_current_release_archive_and_checksum(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "RegexBench")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/regexbench/releases/tag/v0.1.4", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/regexbench/releases/download/v0.1.4/RegexBench-v0.1.4.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/regexbench/releases/download/v0.1.4/RegexBench-v0.1.4.zip.sha256", hrefs)
        self.assertFalse(any("regexbench/releases/tag/v0.1.3" in href for href in hrefs))

    def test_shader_triage_card_links_to_current_release_archive_and_checksum(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "ShaderTriage")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/shader-triage/releases/tag/v0.1.2", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/shader-triage/releases/download/v0.1.2/ShaderTriage-v0.1.2.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/shader-triage/releases/download/v0.1.2/ShaderTriage-v0.1.2.zip.sha256", hrefs)
        self.assertFalse(any("shader-triage/releases/" in href and "v0.1.1" in href for href in hrefs))

    def test_voidfall_card_links_to_current_release_archive_and_checksum(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "VOIDFALL: Last Signal")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/voidfall/releases/tag/v1.0.9", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/voidfall/releases/download/v1.0.9/VOIDFALL-v1.0.9.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/voidfall/releases/download/v1.0.9/SHA256SUMS", hrefs)
        self.assertFalse(any("voidfall/releases/" in href and "v1.0.8" in href for href in hrefs))

    def test_mod_threat_lens_cards_link_to_verified_v0111_release(self) -> None:
        html, cards = read_cards()
        matches = [card for card in cards if card["name"] == "Mod Threat Lens"]
        self.assertEqual(len(matches), 2)
        for card in matches:
            links = card["links"]
            assert isinstance(links, list)
            hrefs = {link["href"] for link in links}
            self.assertIn("https://github.com/GhosTnever-lkm/mod-threat-lens/releases/tag/v0.1.11", hrefs)
            self.assertIn("https://github.com/GhosTnever-lkm/mod-threat-lens/releases/download/v0.1.11/mod-threat-lens-v0.1.11.zip", hrefs)
            self.assertIn("https://github.com/GhosTnever-lkm/mod-threat-lens/releases/download/v0.1.11/mod-threat-lens-v0.1.11.zip.sha256", hrefs)
            self.assertFalse(any("mod-threat-lens/releases/tag/v0.1.10" in href for href in hrefs))
        self.assertNotIn("mod-threat-lens/v0.1.10/docs/report-preview.png", html)

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
            "ModRelease Studio": "v0.3.91",
            "ModRelease Gate": "v1.0.73",
            "Paradox Mod Quality Gate": "v1.0.79",
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
        archive = next(link for link in links if link["href"].endswith("/mod-observatory-0.2.5.zip"))
        checksum = next(link for link in links if link["href"].endswith("/SHA256SUMS.txt"))
        self.assertEqual(release["href"], "https://github.com/GhosTnever-lkm/mod-observatory/releases/tag/v0.2.5")
        self.assertIn("v0.2.5", release["text"])
        self.assertEqual(archive["href"], "https://github.com/GhosTnever-lkm/mod-observatory/releases/download/v0.2.5/mod-observatory-0.2.5.zip")
        self.assertEqual(checksum["href"], "https://github.com/GhosTnever-lkm/mod-observatory/releases/download/v0.2.5/SHA256SUMS.txt")
        self.assertNotIn("v0.2.4", release["href"] + archive["href"] + checksum["href"])

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
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/tag/v0.4.5",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/download/v0.4.5/Mod-Conflict-Map-v0.4.5.zip",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/paradox-mod-conflict-map/releases/download/v0.4.5/Mod-Conflict-Map-v0.4.5.zip.sha256",
            {link["href"] for link in links},
        )

    def test_contrastkit_links_to_current_published_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "ContrastKit")
        hrefs = {link["href"] for link in card["links"]}
        self.assertIn("https://github.com/GhosTnever-lkm/contrastkit/releases/tag/v1.0.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/contrastkit/releases/download/v1.0.3/ContrastKit-v1.0.3.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/contrastkit/releases/download/v1.0.3/ContrastKit-v1.0.3.zip.sha256", hrefs)

    def test_captionlint_links_to_current_published_release_assets(self) -> None:
        html, cards = read_cards()
        project_card_count = len(re.findall(r'<article\b[^>]*class="[^"]*\bproject-card\b', html))
        self.assertEqual(len(cards), project_card_count)
        card = next(card for card in cards if card["name"] == "CaptionLint")
        self.assertTrue(any(link["href"].endswith("/releases/tag/v1.0.6") for link in card["links"]))
        self.assertIn("Clausewitz Log Doctor", {str(card["name"]) for card in cards})
        hrefs = set(re.findall(r'https://github\.com/GhosTnever-lkm/subtitle-release-gate/[^" ]+', html))
        self.assertIn("https://github.com/GhosTnever-lkm/subtitle-release-gate/releases/tag/v1.0.6", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/subtitle-release-gate/releases/download/v1.0.6/CaptionLint-v1.0.6.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/subtitle-release-gate/releases/download/v1.0.6/CaptionLint-v1.0.6.zip.sha256", hrefs)
        self.assertFalse(any("subtitle-release-gate/releases/" in href and ("v1.0.5" in href or "v1.0.4" in href) for href in hrefs))

    def test_asset_sieve_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Asset Sieve")
        links = card["links"]
        assert isinstance(links, list)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/asset-sieve/releases/tag/v0.1.7",
            {link["href"] for link in links},
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/asset-sieve/releases/download/v0.1.7/asset_sieve-0.1.7-py3-none-any.whl",
            {link["href"] for link in links},
        )
        self.assertFalse(any("asset-sieve/releases/tag/v0.1.6" in link["href"] for link in links))

    def test_agent_run_lens_links_to_its_published_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Agent Run Lens")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/agent-run-lens/releases/tag/v1.0.2", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/agent-run-lens/releases/download/v1.0.2/Agent-Run-Lens-v1.0.2.zip", hrefs)
        self.assertFalse(any("agent-run-lens/releases/tag/v1.0.1" in href for href in hrefs))

    def test_audioscribe_links_to_its_published_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "AudioScribe Studio")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/audioscribe-studio/releases/tag/v0.1.9", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/audioscribe-studio/releases/download/v0.1.9/AudioScribe-Studio-v0.1.9.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/audioscribe-studio/releases/download/v0.1.9/AudioScribe-Studio-v0.1.9.zip.sha256", hrefs)
        self.assertNotIn("v0.1.8", " ".join(hrefs))
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
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/subtitle-timing-studio/releases/tag/v1.0.8", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/subtitle-timing-studio/releases/download/v1.0.8/Subtitle-Timing-Studio-1.0.8.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/subtitle-timing-studio/releases/download/v1.0.8/Subtitle-Timing-Studio-1.0.8.zip.sha256", hrefs)
        self.assertFalse(any("subtitle-timing-studio/releases/tag/v1.0.7" in href for href in hrefs))
    def test_captionbench_links_to_its_current_release_and_archive(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "CaptionBench")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/captionbench/releases/tag/v0.1.5", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/captionbench/releases/download/v0.1.5/CaptionBench-v0.1.5.zip", hrefs)
        self.assertFalse(any("captionbench/releases/tag/v0.1.2" in href for href in hrefs))

    def test_harbortrace_links_to_its_current_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "HarborTrace")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/harbortrace/releases/tag/v0.1.4", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/harbortrace/releases/download/v0.1.4/HarborTrace-v0.1.4.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/harbortrace/releases/download/v0.1.4/HarborTrace-v0.1.4.zip.sha256", hrefs)
        self.assertFalse(any("harbortrace/releases/tag/v0.1.3" in href for href in hrefs))

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
        self.assertIn("https://github.com/GhosTnever-lkm/tabharbor/releases/tag/v0.1.4", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/tabharbor/releases/download/v0.1.4/TabHarbor-v0.1.4.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/tabharbor/releases/download/v0.1.4/TabHarbor-v0.1.4.sha256", hrefs)
        self.assertFalse(any("tabharbor/releases/tag/v0.1.3" in href for href in hrefs))
        self.assertIn("100", html)

    def test_saveharbor_links_to_its_current_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "SaveHarbor")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/saveharbor/releases/tag/v1.1.2", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/saveharbor/releases/download/v1.1.2/SaveHarbor-v1.1.2.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/saveharbor/releases/download/v1.1.2/SaveHarbor-v1.1.2.sha256", hrefs)
        self.assertFalse(any("saveharbor/releases/tag/v1.1.1" in href for href in hrefs))

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

    def test_quoteforge_card_links_to_current_v013_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "QuoteForge")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/quote-forge/releases/tag/v0.1.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/quote-forge/releases/download/v0.1.3/QuoteForge-v0.1.3.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/quote-forge/releases/download/v0.1.3/QuoteForge-v0.1.3.sha256", hrefs)
        self.assertFalse(any("quote-forge/releases/tag/v0.1.2" in href for href in hrefs))

    def test_pantrypilot_card_links_to_current_v014_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "PantryPilot")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/pantrypilot/releases/tag/v0.1.4", hrefs)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/pantrypilot/releases/download/v0.1.4/PantryPilot-v0.1.4.zip",
            hrefs,
        )
        self.assertFalse(any("pantrypilot/releases/tag/v0.1.3" in href for href in hrefs))

    def test_modpack_inspector_links_to_current_v013_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "ModPack Inspector")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/modpack-inspector/releases/tag/v0.1.3", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/modpack-inspector/releases/latest/download/ModPack-Inspector-0.1.3.zip", hrefs)
        self.assertFalse(any("modpack-inspector/releases/tag/v0.1.2" in href for href in hrefs))

    def test_localelens_links_to_current_v016_release_and_archive(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "LocaleLens")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/localelens/releases/tag/v0.1.6", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/localelens/archive/refs/tags/v0.1.6.zip", hrefs)
        self.assertFalse(any("localelens/releases/tag/v0.1.5" in href for href in hrefs))

    def test_aegisscan_links_to_current_v014_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "AegisScan AV")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/aegisscan-av/releases/tag/v0.1.4", hrefs)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/aegisscan-av/releases/download/v0.1.4/aegisscan_av-0.1.4-py3-none-any.whl",
            hrefs,
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/aegisscan-av/releases/download/v0.1.4/SHA256SUMS.txt",
            hrefs,
        )
        self.assertFalse(any("aegisscan-av/releases/tag/v0.1.3" in href for href in hrefs))

    def test_csv_key_diff_card_uses_current_v015_assets_and_preview(self) -> None:
        html, cards = read_cards()
        card = next(card for card in cards if card["name"] == "CSV Key Diff")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/csv-key-diff/releases/tag/v0.1.5", hrefs)
        self.assertIn(
            "https://github.com/GhosTnever-lkm/csv-key-diff/releases/download/v0.1.5/csv-key-diff-v0.1.5.zip",
            hrefs,
        )
        self.assertIn(
            "https://github.com/GhosTnever-lkm/csv-key-diff/releases/download/v0.1.5/csv-key-diff-v0.1.5.zip.sha256",
            hrefs,
        )
        self.assertIn("https://raw.githubusercontent.com/GhosTnever-lkm/csv-key-diff/v0.1.5/docs/demo.svg", html)
        self.assertFalse(any("csv-key-diff/releases/tag/v0.1.4" in href for href in hrefs))

    def test_riftunpack_card_links_to_current_v106_binaries_and_checksum(self) -> None:
        html, cards = read_cards()
        card = next(card for card in cards if card["name"] == "RiftUnpack")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/RiftUnpack/releases/tag/v1.0.6", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/RiftUnpack/releases/download/v1.0.6/RiftUnpack.exe", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/RiftUnpack/releases/download/v1.0.6/RiftUnpack-GUI.exe", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/RiftUnpack/releases/download/v1.0.6/SHA256SUMS.txt", hrefs)
        self.assertIn("https://raw.githubusercontent.com/GhosTnever-lkm/RiftUnpack/v1.0.6/docs/images/gui-screenshot.png", html)
        self.assertFalse(any("RiftUnpack/releases/tag/v1.0.5" in href for href in hrefs))
        self.assertNotIn("https://raw.githubusercontent.com/GhosTnever-lkm/RiftUnpack/v1.0.4/docs/images/gui-screenshot.png", html)
        self.assertFalse(any("RiftUnpack/releases/tag/v1.0.4" in href for href in hrefs))

    def test_gamepad_lab_card_links_to_current_v104_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Gamepad Lab")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/gamepad-lab/releases/tag/v1.0.4", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/gamepad-lab/releases/download/v1.0.4/Gamepad-Lab-v1.0.4.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/gamepad-lab/releases/download/v1.0.4/Gamepad-Lab-v1.0.4.zip.sha256", hrefs)
        self.assertFalse(any("gamepad-lab/releases/tag/v1.0.3" in href for href in hrefs))

    def test_pingscope_card_links_to_current_v024_windows_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "PingScope")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/ping-scope/releases/tag/v0.2.4", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/ping-scope/releases/download/v0.2.4/PingScope-v0.2.4-windows-x64.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/ping-scope/releases/download/v0.2.4/PingScope-v0.2.4-windows-x64.zip.sha256", hrefs)
        self.assertFalse(any("ping-scope/releases/tag/v0.2.3" in href for href in hrefs))

    def test_tracked_artifacts_card_links_to_current_v014_wheel_and_checksum(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "tracked-artifacts-check")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/tracked-artifacts-check/releases/tag/v0.1.4", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/tracked-artifacts-check/releases/download/v0.1.4/tracked_artifacts_check-0.1.4-py3-none-any.whl", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/tracked-artifacts-check/releases/download/v0.1.4/SHA256SUMS.txt", hrefs)
        self.assertFalse(any("tracked-artifacts-check/releases/tag/v0.1.2" in href for href in hrefs))

    def test_pages_workflow_checks_pull_requests_without_deploying_them(self) -> None:
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertRegex(workflow, r"(?m)^  pull_request:")
        self.assertRegex(workflow, r"(?m)^  validate:")
        self.assertRegex(workflow, r"(?m)^    needs: validate$")
        self.assertRegex(
            workflow,
            r"(?m)^    if: github\.event_name != 'pull_request' && github\.ref == 'refs/heads/main'$")

    def test_clausewitz_log_doctor_links_to_verified_v021_release_assets(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "Clausewitz Log Doctor")
        links = card["links"]
        assert isinstance(links, list)
        hrefs = {link["href"] for link in links}
        self.assertIn("https://github.com/GhosTnever-lkm/clausewitz-log-doctor/releases/tag/v0.2.1", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/clausewitz-log-doctor/releases/download/v0.2.1/clausewitz-log-doctor-0.2.1.zip", hrefs)
        self.assertIn("https://github.com/GhosTnever-lkm/clausewitz-log-doctor/releases/download/v0.2.1/clausewitz-log-doctor-0.2.1.zip.sha256", hrefs)
        self.assertFalse(any("clausewitz-log-doctor/releases/tag/v0.2.0" in href for href in hrefs))

    def test_diffshield_action_card_links_to_current_release(self) -> None:
        _, cards = read_cards()
        card = next(card for card in cards if card["name"] == "DiffShield Action")
        links = card["links"]
        assert isinstance(links, list)
        release = next(link for link in links if "/diffshield-action/releases/tag/" in link["href"])
        self.assertEqual(
            release["href"],
            "https://github.com/GhosTnever-lkm/diffshield-action/releases/tag/v1.0.5",
        )
        self.assertEqual(release["text"].strip(), "Релиз v1.0.5 ↗")


if __name__ == "__main__":
    unittest.main()
