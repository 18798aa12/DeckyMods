import { PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { useState } from "react";
import { backend } from "./rpc";
import { Action, Note } from "./controls";
import { PlanTargets } from "./PlanTargets";
import { formatBytes, openNexus, safeError } from "./state";
import type { Game, Job, Plan, RunAction } from "./types";
const phaseLabels: Record<Job["phase"], string> = {
  queued: "排队中",
  awaiting_browser: "等待网页授权所选文件",
  downloading: "下载中",
  scanning: "检查压缩包",
  ready: "等待安装确认",
  installing: "安装中",
  complete: "已完成",
  failed: "失败",
  cancelled: "已取消",
};
interface Props {
  readonly jobs: readonly Job[];
  readonly games: readonly Game[];
  readonly busy: boolean;
  readonly run: RunAction;
  readonly onJob: (job: Job) => void;
}
export function JobPanel({ jobs, games, busy, run, onJob }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [acknowledged, setAcknowledged] = useState(false);
  const planReady = jobs.some(
    (job) => job.plan_id === plan?.id && job.phase === "ready",
  );
  const target = games.find((game) => game.id === plan?.game_id);
  const deploymentBlocked =
    !target?.installed || target.running || target.updating;
  return (
    <PanelSection title="下载与安装任务">
      <Action onClick={() => setExpanded(!expanded)}>
        {expanded
          ? "收起下载与安装任务"
          : `展开下载与安装任务（${jobs.length}）`}
      </Action>
      {expanded && (
        <>
          {jobs.length === 0 && (
            <Note>还没有任务。先选择游戏，再获取 MOD 或导入本地压缩包。</Note>
          )}
          {jobs.map((job) => (
            <div key={job.id}>
              <Note>
                {job.name} · {phaseLabels[job.phase]}
                {job.bytes_total > 0 && (
                  <>
                    <br />
                    {formatBytes(job.bytes_done)} /{" "}
                    {formatBytes(job.bytes_total)}
                  </>
                )}
                {job.error && (
                  <>
                    <br />
                    {safeError(job.error)}
                  </>
                )}
              </Note>
              {job.phase === "awaiting_browser" && (
                <Note>
                  正在等待所选文件的网页授权，不代表 API Key 无效。
                  请在网页登录与 API 绑定相同的 Nexus 账号并确认下载；
                  Steam 内置浏览器与 Chrome / Firefox 可能需要分别登录。
                </Note>
              )}
              {job.bytes_total > 0 && job.phase === "downloading" && (
                <PanelSectionRow>
                  <progress
                    aria-label={`${job.name} 下载进度`}
                    max={job.bytes_total}
                    value={job.bytes_done}
                  />
                </PanelSectionRow>
              )}
              {job.browser_url && job.phase === "awaiting_browser" && (
                <Action
                  disabled={busy}
                  onClick={() => {
                    void run("已打开文件下载页", async () => {
                      openNexus(job.browser_url as string);
                      return true;
                    });
                  }}
                >
                  继续在 Nexus 网页确认
                </Action>
              )}
              {job.phase === "ready" && job.plan_id && (
                <Action
                  disabled={busy}
                  onClick={() => {
                    void run(
                      "安装预览已加载",
                      () => backend.getPlan(job.plan_id as string),
                      (next) => {
                        setPlan(next);
                        setAcknowledged(false);
                      },
                    );
                  }}
                >
                  预览安装
                </Action>
              )}
              {[
                "queued",
                "awaiting_browser",
                "downloading",
                "scanning",
                "ready",
              ].includes(job.phase) && (
                <Action
                  disabled={busy}
                  onClick={() => {
                    void run(
                      "任务已取消",
                      () => backend.cancelJob(job.id),
                      onJob,
                    );
                  }}
                >
                  取消“{job.name}”
                </Action>
              )}
            </div>
          ))}
          {plan && (
            <>
              <Note>
                安装预览：{plan.name}
                <br />
                {plan.files_count} 个文件 · {formatBytes(plan.bytes)}
                <br />
                安装前请先退出游戏。
              </Note>
              <PlanTargets key={plan.id} targets={plan.targets ?? []} />
              {target?.updating && (
                <Note>Steam 更新中，请等待更新完成后再安装 MOD。</Note>
              )}
              {target?.running && (
                <Note>游戏正在运行，请先退出游戏再安装 MOD。</Note>
              )}
              {plan.requirements.map((item, index) => (
                <Note key={`requirement-${index}`}>{item}</Note>
              ))}
              {plan.warnings.map((item, index) => (
                <Note key={`warning-${index}`}>{item}</Note>
              ))}
              {plan.blocked_reason && <Note>{plan.blocked_reason}</Note>}
              {plan.conflicts.length > 0 && (
                <>
                  <Note>
                    以下目标存在冲突。确认后原文件会进入备份，禁用或卸载时按部署记录恢复。
                  </Note>
                  {plan.conflicts.map((item, index) => (
                    <Note key={`conflict-${index}`}>{item}</Note>
                  ))}
                  <PanelSectionRow>
                    <ToggleField
                      label="我确认覆盖上述冲突文件"
                      checked={acknowledged}
                      disabled={busy}
                      onChange={setAcknowledged}
                    />
                  </PanelSectionRow>
                </>
              )}
              <Action
                disabled={
                  busy ||
                  deploymentBlocked ||
                  !planReady ||
                  !plan.can_install ||
                  (plan.conflicts.length > 0 && !acknowledged)
                }
                onClick={() => {
                  void run(
                    "安装任务已创建",
                    () => backend.installPlan(plan.id, acknowledged),
                    (job) => {
                      onJob(job);
                      setPlan(null);
                      setAcknowledged(false);
                    },
                  );
                }}
              >
                确认安装
              </Action>
              <Action
                disabled={busy}
                onClick={() => {
                  setPlan(null);
                  setAcknowledged(false);
                }}
              >
                关闭安装预览
              </Action>
            </>
          )}
        </>
      )}
    </PanelSection>
  );
}
