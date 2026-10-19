import { Navigation } from "@decky/ui";

// Curated documentation hosts, including exact project-owned GitHub Pages sites.
// Arbitrary *.github.io or subdomains are deliberately not treated as official.
const GUIDE_HOSTS = new Set([
  "github.com", "www.nexusmods.com", "nexusmods.com", "forums.nexusmods.com",
  "docs.bepinex.dev", "thunderstore.io", "wiki.thunderstore.io", "smapi.io",
  "stardewvalleywiki.com", "wiki.stardewvalley.net", "wiki.factorio.com",
  "prismlauncher.org", "skylines.paradoxwikis.com", "pzwiki.net",
  "docs.ficsit.app", "ficsit.app", "smm.ficsit.app", "dredgemods.com",
  "tonimacaroni.github.io", "starlight.sr2.dev", "modapi.survivetheforest.net",
  "rimsort.github.io", "terraria.wiki.gg", "hollowknight-modding.github.io",
  "wiki.redmodding.org", "modorganizer.org", "tes5edit.github.io",
  "docs.ue4ss.com", "docs.dalamud.net", "wiki.bg3.community",
  "docs.larian.game", "mod.io", "store.steampowered.com",
  "skse.silverlock.org", "f4se.silverlock.org",
]);

export function safeGuideLink(value: string): string | null {
  if (value.length > 2048 || /[\s\\]/u.test(value)) return null;
  try {
    const url = new URL(value);
    if (
      url.protocol !== "https:" || !GUIDE_HOSTS.has(url.hostname) ||
      url.username || url.password || url.port || url.search ||
      /(?:key|token|signature|auth|password|credential|code)\s*[:=]/iu.test(decodeURIComponent(url.hash))
    ) return null;
    return url.href;
  } catch {
    return null;
  }
}

export function openGuideLink(value: string): boolean {
  const url = safeGuideLink(value);
  if (!url) return false;
  Navigation.NavigateToExternalWeb(url);
  return true;
}
