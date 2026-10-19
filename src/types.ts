export interface Auth {
  readonly connected: boolean;
  readonly name: string | null;
  readonly premium: boolean;
  readonly user_id: number | null;
  readonly error: string | null;
}
export interface Handler {
  readonly enabled: boolean;
  readonly supported: boolean;
  readonly previous: string | null;
  readonly message: string | null;
}
export interface Game {
  readonly id: string;
  readonly name: string;
  readonly series: string;
  readonly series_name: string;
  readonly nexus_domain: string;
  readonly steam_app_ids: readonly string[];
  readonly adapter: string;
  readonly support: "automatic" | "needs_setup" | "catalog";
  readonly requirements: readonly string[];
  readonly sources: readonly string[];
  readonly installed: boolean;
  readonly path: string | null;
  readonly app_id: string | null;
  readonly build_id: string | null;
  readonly running: boolean;
  readonly updating?: boolean;
  readonly manual_root?: boolean;
  readonly root_error?: string | null;
}
export interface Mod {
  readonly id: string;
  readonly name: string;
  readonly enabled: boolean;
  readonly installed_at: string;
  readonly files_count: number;
  readonly nexus_mod_id: number | null;
  readonly nexus_file_id: number | null;
  readonly source_url: string | null;
}
export type InstallMode = "auto" | "game_root" | `method:${string}`;
export interface InstallGuide {
  readonly game_id: string;
  readonly name: string;
  readonly checked_at: string;
  readonly notes: readonly string[];
  readonly sources: readonly string[];
  readonly methods: readonly {
    readonly id: string;
    readonly label: string;
    readonly versions: readonly string[];
    readonly format: string;
    readonly destination: string;
    readonly requirements: readonly string[];
    readonly source_urls: readonly string[];
    readonly can_install: boolean;
    readonly install_mode: InstallMode | null;
  }[];
}
export interface ModDetails {
  readonly name: string;
  readonly author: string | null;
  readonly version: string | null;
  readonly description: string;
  readonly source_url: string | null;
  readonly origin: string;
  readonly error: string | null;
}
export interface GameView {
  readonly game: Game;
  readonly mods: readonly Mod[];
  readonly recovery_error: string | null;
}
export interface LaunchSetup {
  readonly supported: boolean;
  readonly required: boolean;
  readonly reason: string;
  readonly app_id: string | null;
  readonly auto_enabled: boolean;
  readonly backup_available: boolean;
}
export interface ResidentStatus {
  readonly supported: boolean;
  readonly family: string;
  readonly build_id: string | null;
  readonly runtime_tdb: number | null;
  readonly renderer: string | null;
  readonly runtime_evidence: boolean;
  readonly script_count: number;
  readonly last_run_at: string | null;
  readonly loader_present: boolean;
  readonly config_exists: boolean;
  readonly config_valid: boolean;
  readonly loose_enabled: boolean;
  readonly pak_directory_enabled: boolean;
  readonly config_backup_available: boolean;
  readonly warnings: readonly string[];
}
export interface UpdateStatus {
  readonly current_version: string;
  readonly latest_version: string | null;
  readonly available: boolean;
  readonly checked_at: string | null;
  readonly error: string | null;
  readonly source: string | null;
  readonly auto_check: boolean;
  readonly source_label: string;
}
export interface UpdateArtifact {
  readonly artifact: string;
  readonly version: string;
  readonly sha256: string;
}
export interface LaunchChange {
  readonly id: string;
  readonly app_id: string;
  readonly before: string;
  readonly after: string;
  readonly changed: boolean;
}
export interface NexusFile {
  readonly file_id: number;
  readonly name: string;
  readonly version: string;
  readonly category: string;
  readonly size_bytes: number;
  readonly description: string;
  readonly primary: boolean;
}
export interface NexusMod {
  readonly game_id: string;
  readonly mod_id: number;
  readonly name: string;
  readonly author: string;
  readonly summary: string;
  readonly page_url: string;
  readonly files: readonly NexusFile[];
}
export interface Job {
  readonly id: string;
  readonly game_id: string;
  readonly name: string;
  readonly phase:
    | "queued"
    | "awaiting_browser"
    | "downloading"
    | "scanning"
    | "ready"
    | "installing"
    | "complete"
    | "failed"
    | "cancelled";
  readonly bytes_done: number;
  readonly bytes_total: number;
  readonly error: string | null;
  readonly plan_id: string | null;
  readonly browser_url: string | null;
}
export interface Plan {
  readonly id: string;
  readonly game_id: string;
  readonly name: string;
  readonly files_count: number;
  readonly targets?: readonly string[];
  readonly bytes: number;
  readonly conflicts: readonly string[];
  readonly warnings: readonly string[];
  readonly requirements: readonly string[];
  readonly config_requirements?: readonly string[];
  readonly blocked_reason: string | null;
  readonly can_install: boolean;
}
export interface Status {
  readonly version: string;
  readonly platform_supported: boolean;
  readonly auth: Auth;
  readonly jobs: readonly Job[];
  readonly handler: Handler;
  readonly error: string | null;
}
export type Result<T> =
  | { readonly ok: true; readonly data: T }
  | { readonly ok: false; readonly error: string };
export type RunAction = <T>(
  label: string,
  operation: () => Promise<T>,
  onSuccess?: (result: T) => void,
) => Promise<T | null>;
