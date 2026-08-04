export type IncidentStatus = "pending" | "diagnosed" | "resolved" | "action_failed";

export type RiskLevel = "low" | "medium" | "high";

export type ApprovalStatus = "pending" | "approved" | "rejected" | "used";

export interface Incident {
  id: number;
  source: string;
  status: IncidentStatus;
  created_at: string;
}

export interface EvidenceRef {
  tool_name: string;
  summary: string;
}

export interface Diagnosis {
  root_cause_hypothesis: string;
  confidence: number;
  risk_level: RiskLevel;
  suggested_action: string | null;
  evidence_refs: { evidence: EvidenceRef[] } | null;
}

export interface Approval {
  status: ApprovalStatus;
  approved_by: string | null;
}

export interface AuditEntry {
  actor: string;
  action: string;
  detail: Record<string, unknown> | null;
  created_at: string;
}

export interface IncidentDetail extends Incident {
  diagnosis: Diagnosis | null;
  approval: Approval | null;
  audit_log: AuditEntry[];
}
