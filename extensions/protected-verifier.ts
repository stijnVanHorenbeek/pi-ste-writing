import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import type { VerificationReport } from "./guard-session.ts";

interface ExecResult {
	code: number;
	stdout: string;
	stderr: string;
}

export type ExecVerifier = (
	command: string,
	args: string[],
	options: { signal?: AbortSignal; timeout: number },
) => Promise<ExecResult>;

function parseReport(stdout: string): VerificationReport {
	let value: unknown;
	try {
		value = JSON.parse(stdout);
	} catch {
		throw new Error("Protected verifier returned malformed JSON");
	}
	if (
		typeof value !== "object" ||
		value === null ||
		typeof (value as { ok?: unknown }).ok !== "boolean" ||
		!Array.isArray((value as { violations?: unknown }).violations)
	) {
		throw new Error("Protected verifier returned an invalid report");
	}
	const report = value as VerificationReport;
	if (report.ok !== (report.violations.length === 0)) {
		throw new Error("Protected verifier returned an invalid report");
	}
	return report;
}

export async function verifyWithPython(
	exec: ExecVerifier,
	scriptPath: string,
	source: string,
	draft: string,
	signal?: AbortSignal,
): Promise<VerificationReport> {
	const directory = await mkdtemp(join(tmpdir(), "pi-clear-writing-"));
	const sourcePath = join(directory, "source.md");
	const draftPath = join(directory, "draft.md");
	try {
		await Promise.all([
			writeFile(sourcePath, source, { encoding: "utf8", mode: 0o600 }),
			writeFile(draftPath, draft, { encoding: "utf8", mode: 0o600 }),
		]);
		const result = await exec(
			"python3",
			[scriptPath, "--source", sourcePath, draftPath],
			{ signal, timeout: 10_000 },
		);
		if (result.code !== 0 && result.code !== 1) {
			throw new Error(
				`Protected verifier failed with exit ${result.code}: ${result.stderr.trim() || "no error text"}`,
			);
		}
		const report = parseReport(result.stdout);
		if ((result.code === 0) !== report.ok) {
			throw new Error("Protected verifier exit status conflicts with report");
		}
		return report;
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}
