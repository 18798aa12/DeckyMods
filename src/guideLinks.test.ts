import data from "../data/install_guides.json";
import { beforeEach, describe, expect, it, vi } from "vitest";

const external = vi.hoisted(() => vi.fn());
vi.mock("@decky/ui", () => ({ Navigation: { NavigateToExternalWeb: external } }));
import { openGuideLink, safeGuideLink } from "./guideLinks";

beforeEach(() => { external.mockReset(); });

describe("installation guide source links", () => {
  it.each([
    "https://github.com/BepInEx/BepInEx/blob/master/README.md#L10",
    "https://docs.bepinex.dev/articles/user_guide/installation/index.html",
    "https://www.nexusmods.com/games/stardewvalley",
    "https://pzwiki.net/wiki/Mod_structure",
    "https://starlight.sr2.dev/docs/installation/linux/steam",
  ])("allows a public official HTTPS reference: %s", (url) => {
    expect(safeGuideLink(url)).toBe(url);
    expect(openGuideLink(url)).toBe(true);
    expect(external).toHaveBeenCalledWith(url);
  });

  it.each([
    "http://github.com/BepInEx/BepInEx",
    "javascript:alert(1)",
    "file:///home/deck/private",
    "https://user:secret@github.com/BepInEx/BepInEx",
    "https://github.com:8443/BepInEx/BepInEx",
    "https://github.com.evil.example/BepInEx",
    "https://github.com./BepInEx",
    "https://127.0.0.1/docs",
    "https://[::1]/docs",
    "https://example.github.io/docs",
    "https://github.com/BepInEx/BepInEx?token=synthetic",
    "https://github.com/BepInEx/BepInEx#access_token=synthetic",
    "https://github.com/BepInEx/BepInEx#token%3Dsynthetic",
    "https://github.com/\nBepInEx/BepInEx",
    "https://github.com\\@127.0.0.1/docs",
    "not a URL",
  ])("never opens an unsafe or credential-bearing link: %s", (url) => {
    expect(safeGuideLink(url)).toBeNull();
    expect(openGuideLink(url)).toBe(false);
    expect(external).not.toHaveBeenCalled();
  });
});


it("can open every source shipped in the researched catalog", () => {
  for (const game of data.games) {
    for (const url of [...game.sources, ...game.methods.flatMap(method => method.source_urls)]) {
      expect(safeGuideLink(url), url).not.toBeNull();
    }
  }
});
