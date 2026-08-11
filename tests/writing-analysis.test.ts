import assert from "node:assert/strict";
import test from "node:test";

import {
	MAX_ANALYSIS_BYTES,
	lintText,
	verifyProtectedContent,
} from "../extensions/writing-analysis.ts";

test("verifier preserves occurrence counts and Markdown containers", () => {
	const accepted = verifyProtectedContent(
		"# Release `OPS-6634`\n\nRun drain-node --ignore-daemonsets at 17:30.",
		"# Release `OPS-6634`\n\nExecute drain-node --ignore-daemonsets at 17:30.",
	);
	assert.equal(accepted.ok, true);
	assert.deepEqual(accepted.violations, []);

	const moved = verifyProtectedContent(
		"# Release `OPS-6634`\n\nRun cleanup.",
		"# Release\n\nRun cleanup for `OPS-6634`.",
	);
	assert.equal(moved.ok, false);
	const inline = moved.violations.find((item) => item.kind === "inline-code");
	assert.equal(inline?.expected[0]?.container, "heading-1");
	assert.equal(inline?.actual[0]?.container, "flow");
});

test("verifier rejects drift for every implemented protected kind", () => {
	const cases = [
		["inline-code", "Use `old`.", "Use `new`."],
		["fenced-code", "```text\nold\n```\n", "```text\nnew\n```\n"],
		["link-destination", "Read [guide](https://example.test/old).", "Read [guide](https://example.test/new)."],
		["quoted-diagnostic", "> Error: lease expired", "> Error: lease was lost"],
		["bare-url", "Read https://example.test/old.", "Read https://example.test/new."],
		["numeric-token", "Run at ١٢:٣٠.", "Run at ١٣:٣٠."],
		["modal-phrase", "Worker must not delete data.", "Worker should delete data."],
		["path", "Copy /srv/releases/old/app.bin.", "Copy /srv/releases/new/app.bin."],
		["cli-flag", "Run drain-node --safe.", "Run drain-node --force."],
		["environment-variable", "Set $RELEASE_ID.", "Set $DEPLOY_ID."],
		["link-label", "Read [Emergency runbook](https://example.test).", "Read [Guide](https://example.test)."],
		["bold-text", "Choose **Witness Matrix**.", "Choose **Witness Table**."],
		["json-key", '{"retry_count": true}', '{"retries": true}'],
		["identifier", "Call ApplyPolicy.", "Call ApplyPolicies."],
	] as const;
	for (const [kind, source, draft] of cases) {
		const report = verifyProtectedContent(source, draft);
		assert.equal(report.ok, false, kind);
		assert.ok(report.violations.some((item) => item.kind === kind), kind);
	}
});

test("verifier handles normalization and parser edge cases", () => {
	assert.equal(
		verifyProtectedContent("Worker must\nnot delete data.", "Worker must not delete data.").ok,
		true,
	);
	assert.equal(
		verifyProtectedContent("Worker MUST NOT delete data.", "Worker must not delete data.").ok,
		false,
	);
	assert.equal(
		verifyProtectedContent("```text\r\nvalue\r\n```\r\n", "```text\nvalue\n```\n").ok,
		true,
	);
	assert.equal(
		verifyProtectedContent("    first\r\n    second\r\n", "    first\n    second\n").ok,
		true,
	);
	assert.equal(
		verifyProtectedContent("Stop service. Drain node.", "1. Stop service.\n2. Drain node.").ok,
		true,
	);
	assert.equal(
		verifyProtectedContent("Use `__proto__` once.", "Use `__proto__` twice: `__proto__`.").ok,
		false,
	);
	const nested = verifyProtectedContent(
		"Read [function docs](https://example.test/fn(a(b))).",
		"Read [function docs](https://example.test/fn(a(c))).",
	);
	assert.ok(nested.violations.some((item) => item.kind === "link-destination"));
});

test("linter masks protected Markdown and reports Unicode locations", () => {
	const report = lintText(
		"Use `you should retry`.\n> Error: You should retry.\nhttps://example.test/should\n\n😀 Client should retry.\n",
		"strict",
		"README.md",
	);
	const modals = report.findings.filter((item) => item.rule === "modal");
	assert.equal(modals.length, 1);
	assert.equal(modals[0]?.text, "should");
	assert.equal(modals[0]?.line, 5);
	assert.equal(modals[0]?.column, 10);
});

test("linter applies procedure ordering and passage-specific sentence limits", () => {
	const procedure = lintText(
		"The service records an event when the job fails. Restart the worker if health checks fail. If health checks fail, restart the worker.",
		"procedure",
		"README.md",
	);
	assert.deepEqual(
		procedure.findings.filter((item) => item.rule === "condition-order").map((item) => item.text),
		["Restart the worker if health checks fail."],
	);

	const strict = lintText(
		"# Retry behavior for failed uploads and delayed network responses\n\n" +
		"Verify the backup status before migration and record the snapshot identifier in the change request for operators to review during recovery. " +
		"The worker records each failed upload and retries it after the configured delay without changing stored request data.",
		"strict",
		"README.md",
	);
	const lengths = strict.findings.filter((item) => item.rule === "sentence-length");
	assert.equal(lengths.length, 1);
	assert.match(lengths[0]!.text, /^Verify the backup/);
});

test("strict linter detects modals, contractions, and Latin abbreviations", () => {
	const report = lintText(
		"It isn't ready. It's blocked. You're waiting. We'll retry. They've stopped. The owner's guide may be current, e.g. today.",
		"strict",
		"README.md",
	);
	assert.deepEqual(
		report.findings.filter((item) => item.rule === "contraction").map((item) => item.text),
		["isn't", "It's", "You're", "We'll", "They've"],
	);
	assert.equal(report.findings.some((item) => item.text === "owner's"), false);
	assert.equal(report.findings.filter((item) => item.rule === "modal").length, 1);
	assert.equal(report.findings.filter((item) => item.rule === "latin-abbreviation").length, 1);
});

test("analysis enforces deterministic size and work limits", () => {
	assert.throws(
		() => verifyProtectedContent("x".repeat(MAX_ANALYSIS_BYTES + 1), "x"),
		/exceeds.*limit/i,
	);
	assert.throws(
		() => verifyProtectedContent("1 ".repeat(100_001), "1 ".repeat(100_001)),
		/work limit/i,
	);
	const malformed = "[](".repeat(24_000);
	assert.equal(verifyProtectedContent(malformed, malformed).ok, true);
});

test("verifier states its semantic limitation", () => {
	const report = verifyProtectedContent(
		"Minimum is `low`; maximum is `high`.",
		"Minimum is `high`; maximum is `low`.",
	);
	assert.equal(report.ok, true);
	assert.match(report.disclaimer, /does not prove semantic equivalence/i);
});
