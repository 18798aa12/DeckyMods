import { callable } from "@decky/api";
import { unwrap } from "./state";
import type {
  Auth,
  Game,
  GameView,
  InstallMode,
  ModDetails,
  Handler,
  Job,
  LaunchChange,
  LaunchSetup,
  NexusMod,
  Plan,
  ResidentStatus,
  UpdateStatus,
  UpdateArtifact,
  Result,
  Status,
} from "./types";
const getStatus = callable<[], Result<Status>>("get_status");
const listGames = callable<[], Result<Game[]>>("list_games");
const getGame = callable<[string], Result<GameView>>("get_game");
const getModDetails = callable<[string, string], Result<ModDetails>>("get_mod_details");
const setGameRoot = callable<[string, "auto" | "manual", string], Result<GameView>>("set_game_root");
const getResidentStatus = callable<[string], Result<ResidentStatus>>("get_resident_status");
const prepareResidentSettings = callable<[string, boolean], Result<ResidentStatus>>("prepare_resident_settings");
const restoreResidentSettings = callable<[string], Result<ResidentStatus>>("restore_resident_settings");
const getUpdateStatus = callable<[], Result<UpdateStatus>>("get_update_status");
const setUpdateOptions = callable<[string, boolean], Result<UpdateStatus>>("set_update_options");
const checkUpdate = callable<[], Result<UpdateStatus>>("check_update");
const prepareUpdate = callable<[], Result<UpdateArtifact>>("prepare_update");
const getLaunchSetup = callable<[string], Result<LaunchSetup>>("get_launch_setup");
const setLaunchAuto = callable<[string, boolean], Result<LaunchSetup>>("set_launch_auto");
const prepareLaunchOptions = callable<[string, string, boolean], Result<LaunchChange>>(
  "prepare_launch_options",
);
const finishLaunchOptions = callable<[string, string, string], Result<LaunchSetup>>(
  "finish_launch_options",
);
const bindAccount = callable<[string], Result<Auth>>("bind_account");
const disconnectAccount = callable<[], Result<Auth>>("disconnect_account");
const resolveMod = callable<[string, string], Result<NexusMod>>("resolve_mod");
const beginDownload = callable<[string, number, number, InstallMode?], Result<Job>>(
  "begin_download",
);
const acceptNxm = callable<[string, InstallMode?, string?], Result<Job>>("accept_nxm");
const getImportDirectory = callable<[], Result<string>>("get_import_directory");
const importArchive = callable<[string, string, string, InstallMode?], Result<Job>>(
  "import_archive",
);
const getPlan = callable<[string], Result<Plan>>("get_plan");
const installPlan = callable<[string, boolean], Result<Job>>("install_plan");
const setModEnabled = callable<[string, string, boolean], Result<GameView>>(
  "set_mod_enabled",
);
const uninstallMod = callable<[string, string], Result<GameView>>(
  "uninstall_mod",
);
const getJobs = callable<[], Result<Job[]>>("get_jobs");
const cancelJob = callable<[string], Result<Job>>("cancel_job");
const setNxmHandler = callable<[boolean], Result<Handler>>("set_nxm_handler");
export const backend = {
  getStatus: async (): Promise<Status> => unwrap(await getStatus()),
  listGames: async (): Promise<Game[]> => unwrap(await listGames()),
  getGame: async (id: string): Promise<GameView> => unwrap(await getGame(id)),
  getModDetails: async (game: string, mod: string): Promise<ModDetails> => unwrap(await getModDetails(game, mod)),
  setGameRoot: async (game: string, mode: "auto" | "manual", path = ""): Promise<GameView> => unwrap(await setGameRoot(game, mode, path)),
  getResidentStatus: async (id: string): Promise<ResidentStatus> => unwrap(await getResidentStatus(id)),
  prepareResidentSettings: async (id: string, pak: boolean): Promise<ResidentStatus> => unwrap(await prepareResidentSettings(id, pak)),
  restoreResidentSettings: async (id: string): Promise<ResidentStatus> => unwrap(await restoreResidentSettings(id)),
  getUpdateStatus: async (): Promise<UpdateStatus> => unwrap(await getUpdateStatus()),
  setUpdateOptions: async (source: string, auto: boolean): Promise<UpdateStatus> => unwrap(await setUpdateOptions(source, auto)),
  checkUpdate: async (): Promise<UpdateStatus> => unwrap(await checkUpdate()),
  prepareUpdate: async (): Promise<UpdateArtifact> => unwrap(await prepareUpdate()),
  getLaunchSetup: async (id: string): Promise<LaunchSetup> => unwrap(await getLaunchSetup(id)),
  setLaunchAuto: async (id: string, enabled: boolean): Promise<LaunchSetup> =>
    unwrap(await setLaunchAuto(id, enabled)),
  prepareLaunchOptions: async (id: string, current: string, restore = false): Promise<LaunchChange> =>
    unwrap(await prepareLaunchOptions(id, current, restore)),
  finishLaunchOptions: async (id: string, change: string, observed: string): Promise<LaunchSetup> =>
    unwrap(await finishLaunchOptions(id, change, observed)),
  bindAccount: async (key: string): Promise<Auth> =>
    unwrap(await bindAccount(key)),
  disconnectAccount: async (): Promise<Auth> =>
    unwrap(await disconnectAccount()),
  resolveMod: async (game: string, reference: string): Promise<NexusMod> =>
    unwrap(await resolveMod(game, reference)),
  beginDownload: async (
    game: string,
    mod: number,
    file: number,
    mode?: InstallMode,
  ): Promise<Job> => unwrap(await beginDownload(game, mod, file, mode ?? "auto")),
  acceptNxm: async (uri: string, mode?: InstallMode, game?: string): Promise<Job> => unwrap(await acceptNxm(uri, mode ?? "auto", game)),
  getImportDirectory: async (): Promise<string> =>
    unwrap(await getImportDirectory()),
  importArchive: async (
    game: string,
    path: string,
    name: string,
    mode?: InstallMode,
  ): Promise<Job> => unwrap(await importArchive(game, path, name, mode ?? "auto")),
  getPlan: async (id: string): Promise<Plan> => unwrap(await getPlan(id)),
  installPlan: async (id: string, conflicts: boolean): Promise<Job> =>
    unwrap(await installPlan(id, conflicts)),
  setModEnabled: async (
    game: string,
    mod: string,
    enabled: boolean,
  ): Promise<GameView> => unwrap(await setModEnabled(game, mod, enabled)),
  uninstallMod: async (game: string, mod: string): Promise<GameView> =>
    unwrap(await uninstallMod(game, mod)),
  getJobs: async (): Promise<Job[]> => unwrap(await getJobs()),
  cancelJob: async (id: string): Promise<Job> => unwrap(await cancelJob(id)),
  setNxmHandler: async (enabled: boolean): Promise<Handler> =>
    unwrap(await setNxmHandler(enabled)),
};
