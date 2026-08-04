import { useState } from "react";
import { approveAction, rejectAction, ApiError } from "../api/client";
import type { Approval } from "../types";

interface ApprovalActionsProps {
  incidentId: number;
  approval: Approval | null;
  onResolved: () => Promise<void> | void;
}

type Inflight = "approve" | "reject" | null;

export default function ApprovalActions({ incidentId, approval, onResolved }: ApprovalActionsProps) {
  const [inflight, setInflight] = useState<Inflight>(null);
  const [error, setError] = useState<string | null>(null);

  if (!approval || approval.status !== "pending") {
    return null;
  }

  const handle = async (action: "approve" | "reject") => {
    setInflight(action);
    setError(null);
    try {
      if (action === "approve") {
        await approveAction(incidentId);
      } else {
        await rejectAction(incidentId);
      }
      await onResolved();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Request failed. Please try again.";
      setError(message);
    } finally {
      setInflight(null);
    }
  };

  const disabled = inflight !== null;

  return (
    <div className="rounded-2xl border border-amber-400/20 bg-amber-400/[0.03] p-5">
      <div className="flex items-center gap-2">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-pulse-ring rounded-full bg-amber-400" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-400" />
        </span>
        <h3 className="text-sm font-semibold text-amber-200">Awaiting your approval</h3>
      </div>
      <p className="mt-2 text-sm text-slate-400">
        Sentinel has proposed a remediation. Review the diagnosis and evidence, then approve or reject.
      </p>

      <div className="mt-4 flex gap-3">
        <button
          type="button"
          disabled={disabled}
          onClick={() => handle("approve")}
          className="flex-1 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-emerald-950 transition-all duration-150 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-emerald-500/30 disabled:text-emerald-950/50"
        >
          {inflight === "approve" ? "Approving…" : "Approve"}
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => handle("reject")}
          className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-semibold text-slate-200 transition-all duration-150 hover:bg-slate-800 disabled:cursor-not-allowed disabled:text-slate-500"
        >
          {inflight === "reject" ? "Rejecting…" : "Reject"}
        </button>
      </div>

      {error && (
        <div className="mt-3 rounded-lg border border-rose-500/20 bg-rose-500/5 px-3 py-2 text-xs text-rose-300">
          {error}
        </div>
      )}
    </div>
  );
}
