import assert from "node:assert/strict";
import test from "node:test";

import {
	applyVerification,
	classifySubmissionMessage,
	parseClearWriteArgs,
	repairInstruction,
	startGuard,
} from "../extensions/guard-session.ts";
import { verifyWithPython } from "../extensions/protected-verifier.ts";

const rejected = {
	ok: false,
	violations: [{ kind: "inline-code", expected: [], actual: [] }],
};

test("parses mode while preserving source bytes after delimiter", () => {
	assert.deepEqual(
		parseClearWriteArgs("--mode procedure\n    Run `drain-node --force`.\n"),
		{
			mode: "procedure",
			source: "    Run `drain-node --force`.\n",
		},
	);
	assert.deepEqual(parseClearWriteArgs("   --mode strict Source"), {
		mode: "strict",
		source: "Source",
	});
	assert.deepEqual(parseClearWriteArgs("    indented source"), {
		mode: "clear",
		source: "    indented source",
	});
	assert.deepEqual(parseClearWriteArgs("--mode strict"), {
		mode: "strict",
		source: "",
	});
	assert.deepEqual(parseClearWriteArgs("--model remains source text"), {
		mode: "clear",
		source: "--model remains source text",
	});
	assert.throws(() => parseClearWriteArgs("--mode unsafe source"), /Unknown mode/);
});

test("authorizes exactly one submit call without text or sibling calls", () => {
	assert.deepEqual(
		classifySubmissionMessage(
			[
				{ type: "thinking", thinking: "hidden" },
				{ type: "toolCall", id: "call-1", name: "submit_clear_rewrite" },
			],
			"submit_clear_rewrite",
		),
		{ valid: true, authorizedToolCallId: "call-1" },
	);
	for (const content of [
		[{ type: "text", text: "draft" }],
		[
			{ type: "text", text: "preamble" },
			{ type: "toolCall", id: "call-1", name: "submit_clear_rewrite" },
		],
		[
			{ type: "toolCall", id: "call-1", name: "submit_clear_rewrite" },
			{ type: "toolCall", id: "call-2", name: "submit_clear_rewrite" },
		],
		[
			{ type: "toolCall", id: "call-1", name: "submit_clear_rewrite" },
			{ type: "toolCall", id: "call-2", name: "other_tool" },
		],
	]) {
		assert.equal(
			classifySubmissionMessage(content, "submit_clear_rewrite").valid,
			false,
		);
	}
});

test("guard permits bounded repair then blocks without returning invalid draft", () => {
	let state = startGuard("job-1", "Run `safe-command`.", "clear", 2);

	const retry = applyVerification(state, "Run another command.", rejected);
	assert.equal(retry.status, "retry");
	assert.equal(retry.draft, undefined);
	assert.ok(retry.nextState);

	state = retry.nextState!;
	const blocked = applyVerification(state, "Still wrong.", rejected);
	assert.equal(blocked.status, "blocked");
	assert.equal(blocked.draft, undefined);
	assert.equal(blocked.nextState, undefined);
});

test("guard marks unchanged rejected drafts without retaining draft text", () => {
	let state = startGuard("job-duplicate", "Source", "clear", 4);

	const first = applyVerification(state, "unchanged rejected draft", rejected);
	assert.equal(first.status, "retry");
	assert.equal(first.unchangedDraft, false);
	assert.ok(first.nextState);
	assert.doesNotMatch(JSON.stringify(first.nextState), /unchanged rejected draft/);

	state = first.nextState!;
	const duplicate = applyVerification(state, "unchanged rejected draft", rejected);
	assert.equal(duplicate.status, "retry");
	assert.equal(duplicate.unchangedDraft, true);
	assert.ok(duplicate.nextState);

	state = duplicate.nextState!;
	const revised = applyVerification(state, "revised rejected draft", rejected);
	assert.equal(revised.status, "retry");
	assert.equal(revised.unchangedDraft, false);
});

test("duplicate retry feedback requires changing rejected draft", () => {
	assert.equal(
		repairInstruction("submit_clear_rewrite", false),
		"Protected content verification failed. Repair draft and call submit_clear_rewrite again.",
	);
	assert.match(
		repairInstruction("submit_clear_rewrite", true),
		/Draft is unchanged.*Change draft.*submit_clear_rewrite again/,
	);
});

test("Python verifier receives extension-owned source and candidate files", async () => {
	let observedSource = "";
	let observedDraft = "";
	const report = await verifyWithPython(
		async (_command, args) => {
			const sourceIndex = args.indexOf("--source") + 1;
			observedSource = await import("node:fs/promises").then((fs) =>
				fs.readFile(args[sourceIndex]!, "utf8"),
			);
			observedDraft = await import("node:fs/promises").then((fs) =>
				fs.readFile(args.at(-1)!, "utf8"),
			);
			return {
				code: 0,
				stdout: JSON.stringify({ ok: true, violations: [], disclaimer: "bounded" }),
				stderr: "",
			};
		},
		"/package/protected_verify.py",
		"Trusted source\n",
		"Candidate draft\n",
	);

	assert.equal(observedSource, "Trusted source\n");
	assert.equal(observedDraft, "Candidate draft\n");
	assert.equal(report.ok, true);
});

test("Python verifier fails closed on malformed or conflicting reports", async () => {
	await assert.rejects(
		verifyWithPython(
			async () => ({ code: 0, stdout: "not-json", stderr: "" }),
			"/package/protected_verify.py",
			"source",
			"draft",
		),
		/malformed JSON/,
	);
	await assert.rejects(
		verifyWithPython(
			async () => ({ code: 2, stdout: "", stderr: "python unavailable" }),
			"/package/protected_verify.py",
			"source",
			"draft",
		),
		/exit 2: python unavailable/,
	);
	await assert.rejects(
		verifyWithPython(
			async () => ({
				code: 0,
				stdout: JSON.stringify({ ok: true, violations: [{ kind: "drift" }] }),
				stderr: "",
			}),
			"/package/protected_verify.py",
			"source",
			"draft",
		),
		/invalid report/,
	);
	await assert.rejects(
		verifyWithPython(
			async () => ({
				code: 1,
				stdout: JSON.stringify({ ok: true, violations: [] }),
				stderr: "",
			}),
			"/package/protected_verify.py",
			"source",
			"draft",
		),
		/exit status conflicts/,
	);
});

test("guard returns exact draft only after verifier acceptance", () => {
	const state = startGuard("job-2", "Source", "strict");
	const decision = applyVerification(state, "Accepted draft\n", {
		ok: true,
		violations: [],
	});

	assert.equal(decision.status, "accepted");
	assert.equal(decision.draft, "Accepted draft\n");
	assert.equal(decision.nextState, undefined);
});
