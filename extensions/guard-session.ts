import { createHash } from "node:crypto";

export type WritingMode = "clear" | "procedure" | "strict";

export interface VerificationReport {
	ok: boolean;
	violations: unknown[];
}

export interface GuardState {
	jobId: string;
	source: string;
	mode: WritingMode;
	attempts: number;
	maxAttempts: number;
	lastRejectedDraftSha256?: string;
}

export interface SubmissionDecision {
	status: "accepted" | "retry" | "blocked";
	draft?: string;
	verification: VerificationReport;
	unchangedDraft?: boolean;
	nextState?: GuardState;
}

export function repairInstruction(
	toolName: string,
	unchangedDraft: boolean,
): string {
	if (unchangedDraft) {
		return `Protected content verification failed. Draft is unchanged from previous rejected submission. Change draft to address listed violations, then call ${toolName} again.`;
	}
	return `Protected content verification failed. Repair draft and call ${toolName} again.`;
}

export function classifySubmissionMessage(
	content: Array<{ type: string; id?: string; name?: string }>,
	toolName: string,
): { valid: boolean; authorizedToolCallId?: string } {
	const toolCalls = content.filter((block) => block.type === "toolCall");
	const valid =
		toolCalls.length === 1 &&
		toolCalls[0]?.name === toolName &&
		typeof toolCalls[0]?.id === "string" &&
		content.every(
			(block) =>
				block.type === "thinking" ||
				(block.type === "toolCall" && block.name === toolName),
		);
	return valid
		? { valid: true, authorizedToolCallId: toolCalls[0]!.id }
		: { valid: false };
}

export function parseClearWriteArgs(args: string): {
	mode: WritingMode;
	source: string;
} {
	if (!/^[ \t]*--mode(?:[ \t]|$)/.test(args)) return { mode: "clear", source: args };
	const match = /^[ \t]*--mode[ \t]+(\S+)(?:\r?\n|[ \t]|$)/.exec(args);
	if (!match) throw new Error("Usage: /clear-write [--mode clear|procedure|strict] <source>");
	const mode = match[1];
	if (mode !== "clear" && mode !== "procedure" && mode !== "strict") {
		throw new Error(`Unknown mode: ${mode}`);
	}
	return { mode, source: args.slice(match[0].length) };
}

export function startGuard(
	jobId: string,
	source: string,
	mode: WritingMode,
	maxAttempts = 3,
): GuardState {
	if (maxAttempts < 1 || !Number.isInteger(maxAttempts)) {
		throw new RangeError("maxAttempts must be a positive integer");
	}
	return { jobId, source, mode, attempts: 0, maxAttempts };
}

export function applyVerification(
	state: GuardState,
	draft: string,
	verification: VerificationReport,
): SubmissionDecision {
	if (verification.ok) {
		return { status: "accepted", draft, verification };
	}

	const attempts = state.attempts + 1;
	const draftSha256 = createHash("sha256").update(draft).digest("hex");
	const unchangedDraft = state.lastRejectedDraftSha256 === draftSha256;
	if (attempts >= state.maxAttempts) {
		return { status: "blocked", verification, unchangedDraft };
	}
	return {
		status: "retry",
		verification,
		unchangedDraft,
		nextState: {
			...state,
			attempts,
			lastRejectedDraftSha256: draftSha256,
		},
	};
}
