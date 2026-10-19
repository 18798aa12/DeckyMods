# Third-party notices

DeckyMods is GPL-3.0-only; see LICENSE. No game files, commercial mods, Nexus credentials, or account subscriptions are included.

## Bundled components

- **libarchive-c 5.3**, copyright its contributors, CC0-1.0. Unmodified pure Python modules are bundled; license in `licenses/libarchive-c-LICENSE`. Corresponding wheel and source archive are in the source companion. Native libarchive is supplied by the SteamOS system, not redistributed in this ZIP. https://github.com/Changaco/python-libarchive-c
- **@decky/api 1.1.3**, SteamDeckHomebrew contributors, LGPL-2.1. License in `licenses/decky-api-LICENSE`; matching installed library source in the source companion. The frontend can be rebuilt against modified versions using the included pnpm configuration. https://github.com/SteamDeckHomebrew/loader-api
- **react-icons 5.5.0**, copyright 2018 kamijin_fanta, MIT for library code. Font Awesome 5 icons by Fonticons are CC BY 4.0, https://fontawesome.com/ and https://creativecommons.org/licenses/by/4.0/. License notices and matching used `fa`/library sources accompany the build.
- **tslib 2.8.1**, Microsoft Corporation, Zero-Clause BSD; license and matching sources included.

React, ReactDOM and @decky/ui are supplied by Decky/Steam at runtime, not bundled with the plugin. Their development packages are version-pinned in the lock file.

## Decky Rollup configuration attribution

The small Rollup configuration was adapted from @decky/rollup 1.0.2 (BSD-3-Clause):

Copyright (c) 2024, Steam Deck Homebrew
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Reused project code and research

EditingBoundary, styles, build/test configuration, and their original tests were adapted from **DeckyProxy**, GPL-3.0-only, copyright DeckyProxy contributors. That project's input handling work is reused with the same license. Some deterministic packaging techniques were also informed by its GPL build scripts.

Decky Nexus plugin and official Vortex game extensions were studied as references. Nexus client, Steam discovery, conservative archive mapping, journaled file deployment and recovery here were independently written. Registry entries record factual game IDs, paths and upstream links. No Stellar Blade Vortex extension code or Fluffy binaries are redistributed. REFramework must be obtained separately under its upstream terms.

All names and trademarks belong to their respective owners. This project is not affiliated with Nexus Mods, Valve, or the game publishers.
