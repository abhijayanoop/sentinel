import type { Diagnosis, RiskLevel } from "../types";

interface DiagnosisCardProps {
  diagnosis: Diagnosis | null;
}

const RISK_STYLES: Record<RiskLevel, string> = {
  low: "bg-emerald-400/10 text-emerald-300 ring-1 ring-inset ring-emerald-400/30",
  medium: "bg-amber-400/10 text-amber-300 ring-1 ring-inset ring-amber-400/30",
  high: "bg-rose-400/10 text-rose-300 ring-1 ring-inset ring-rose-400/30",
};

const CONFIDENCE_COLOR = (value: number): string => {
  if (value >= 0.75) return "bg-emerald-400";
  if (value >= 0.45) return "bg-amber-400";
  return "bg-rose-400";
};

export default function DiagnosisCard({ diagnosis }: DiagnosisCardProps) {
  if (!diagnosis) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="text-sm font-semibold text-slate-300">Diagnosis</h3>
        <div className="mt-3 flex items-center gap-2.5 text-sm text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-slate-600" />
          Agent is investigating — no hypothesis yet.
        </div>
      </div>
    );
  }

  const confidencePct = Math.round(diagnosis.confidence * 100);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-300">Diagnosis</h3>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-medium uppercase tracking-wide ${RISK_STYLES[diagnosis.risk_level]}`}
        >
          {diagnosis.risk_level} risk
        </span>
      </div>

      <p className="mt-3 text-[15px] leading-relaxed text-slate-100">
        {diagnosis.root_cause_hypothesis}
      </p>

      <div className="mt-5">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Confidence</span>
          <span className="font-mono text-slate-300">{confidencePct}%</span>
        </div>
        <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${CONFIDENCE_COLOR(diagnosis.confidence)}`}
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>

      {diagnosis.suggested_action && (
        <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3">
          <div className="text-[11px] font-medium uppercase tracking-wide text-slate-500">
            Suggested action
          </div>
          <div className="mt-1 font-mono text-sm text-accent">{diagnosis.suggested_action}</div>
        </div>
      )}
    </div>
  );
}
