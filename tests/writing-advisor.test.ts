import assert from "node:assert/strict";
import { mkdtemp, rm, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

import writingAdvisor from "../extensions/writing-advisor.ts";
import { MAX_ANALYSIS_BYTES } from "../extensions/writing-analysis.ts";

const packageSkillPath = resolve("skills/clear-technical-writing/SKILL.md");
const WRITING_TOOL_NAMES = ["writing_begin", "writing_check"];

type Handler = (event: any, context: any) => any;

interface VisibleEntry {
	value: string;
	valueTruncated: boolean;
	container: string;
	count: number;
	line: number;
	column: number;
}

interface CheckSummary {
	status: string;
	path: string;
	mode?: string;
	sourceExisted?: boolean;
	protectedMatch?: boolean | "not-applicable";
	protectedDeltas?: Array<{ kind: string; removed: VisibleEntry[]; added: VisibleEntry[] }>;
	protectedDeltasTruncated?: boolean;
	hiddenProtectedRemoved?: number;
	hiddenProtectedAdded?: number;
	introducedWarnings?: number;
	preExistingWarnings?: number;
	findings?: Array<{ rule: string; line: number; column: number; text: string; message: string }>;
	findingsTruncated?: boolean;
	next?: string;
	message?: string;
	[key: string]: unknown;
}

function fakePi() {
	const handlers = new Map<string, Handler[]>();
	const tools: any[] = [];
	const commands = new Map<string, any>();
	const messages: string[] = [];
	const notifications: Array<{ message: string; level: string }> = [];
	let active = ["read", "bash", "edit", "write"];
	const discoveredCommands = [{
		name: "skill:clear-technical-writing",
		source: "skill",
		sourceInfo: { path: packageSkillPath, source: "package", scope: "temporary", origin: "package" },
	}];
	const pi = {
		on(name: string, handler: Handler) { handlers.set(name, [...(handlers.get(name) ?? []), handler]); },
		registerTool(tool: any) { tools.push(tool); },
		registerCommand(name: string, command: any) { commands.set(name, command); },
		getActiveTools() { return [...active]; },
		setActiveTools(names: string[]) { active = [...names]; },
		getCommands() { return discoveredCommands; },
		sendUserMessage(message: string) { messages.push(message); },
	};
	return { pi, handlers, tools, commands, messages, notifications, active: () => active };
}

function contextFor(fake: ReturnType<typeof fakePi>, branch: any[] = [], cwd = process.cwd()) {
	return {
		cwd,
		mode: "tui",
		hasUI: true,
		isIdle: () => true,
		sessionManager: { getBranch: () => branch },
		ui: {
			notify(message: string, level: string) { fake.notifications.push({ message, level }); },
			setStatus() {},
		},
	};
}

async function emit(fake: ReturnType<typeof fakePi>, name: string, event: any, branch: any[] = [], cwd = process.cwd()) {
	const context = contextFor(fake, branch, cwd);
	let result;
	for (const handler of fake.handlers.get(name) ?? []) result = await handler(event, context);
	return result;
}

async function activate(fake: ReturnType<typeof fakePi>, cwd = process.cwd()) {
	await emit(fake, "tool_result", {
		toolName: "read",
		input: { path: packageSkillPath },
		isError: false,
		content: [{ type: "text", text: "skill" }],
	}, [], cwd);
}

function tool(fake: ReturnType<typeof fakePi>, name: string) {
	const value = fake.tools.find((candidate) => candidate.name === name);
	assert.ok(value, `missing ${name}`);
	return value;
}

function parseSummary(result: any, status: string): CheckSummary {
	assert.equal(result.content?.[0]?.type, "text");
	const parsed: unknown = JSON.parse(result.content[0].text);
	assert.ok(typeof parsed === "object" && parsed !== null && !Array.isArray(parsed));
	const summary = parsed as CheckSummary;
	assert.equal(summary.status, status);
	assert.equal(typeof summary.path, "string");
	if (["clean", "unchanged", "needs-review"].includes(status)) {
		assert.ok(["clear", "procedure", "strict"].includes(summary.mode ?? ""));
		assert.equal(typeof summary.sourceExisted, "boolean");
		assert.ok(typeof summary.protectedMatch === "boolean" || summary.protectedMatch === "not-applicable");
		assert.ok(Array.isArray(summary.protectedDeltas));
		assert.equal(typeof summary.protectedDeltasTruncated, "boolean");
		for (const key of ["hiddenProtectedRemoved", "hiddenProtectedAdded", "introducedWarnings", "preExistingWarnings"]) {
			assert.equal(typeof summary[key], "number", key);
		}
		assert.ok(Array.isArray(summary.findings));
		assert.equal(typeof summary.findingsTruncated, "boolean");
		assert.equal(typeof summary.next, "string");
	} else {
		assert.equal(typeof summary.message, "string");
	}
	return summary;
}

test("writing tools activate only from package skill provenance and remain additive", async () => {
	const exactRead = fakePi();
	writingAdvisor(exactRead.pi as never);
	assert.equal(exactRead.tools.length, 0);
	await activate(exactRead);
	assert.deepEqual(new Set(exactRead.tools.map((item) => item.name)), new Set(WRITING_TOOL_NAMES));
	assert.ok(["read", "bash", "edit", "write", ...WRITING_TOOL_NAMES].every((name) => exactRead.active().includes(name)));

	for (const event of [
		{ toolName: "read", input: { path: packageSkillPath }, isError: true },
		{ toolName: "read", input: { path: `${packageSkillPath}.bak` }, isError: false },
		{ toolName: "read", input: { path: "/other/clear-technical-writing/SKILL.md" }, isError: false },
	]) {
		const fake = fakePi();
		writingAdvisor(fake.pi as never);
		await emit(fake, "tool_result", event);
		assert.deepEqual(fake.active(), ["read", "bash", "edit", "write"]);
	}

	const lookalike = fakePi();
	writingAdvisor(lookalike.pi as never);
	await emit(lookalike, "input", { text: "/skill:clear-technical-writing-extra improve README", source: "interactive" });
	assert.equal(WRITING_TOOL_NAMES.some((name) => lookalike.active().includes(name)), false);

	const invoked = fakePi();
	writingAdvisor(invoked.pi as never);
	await emit(invoked, "input", { text: "/skill:clear-technical-writing improve README", source: "interactive" });
	assert.ok(WRITING_TOOL_NAMES.every((name) => invoked.active().includes(name)));
});

test("ste_doc accepts one quoted path, rejects invalid paths, and starts normal repository workflow", async () => {
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	await emit(fake, "session_start", { reason: "new" });
	assert.deepEqual([...fake.commands.keys()], ["ste_doc"]);
	await fake.commands.get("ste_doc").handler('"docs/guide one.md"', contextFor(fake));
	assert.equal(fake.messages.length, 1);
	assert.ok(fake.messages[0]!.includes('"docs/guide one.md"'));
	assert.ok(fake.messages[0]!.includes("clear-technical-writing"));
	assert.ok(fake.messages[0]!.includes("writing_begin"));
	assert.ok(fake.messages[0]!.includes("writing_check"));
	assert.ok(["read", "edit", "write", ...WRITING_TOOL_NAMES].every((name) => fake.active().includes(name)));

	for (const path of ["   ", "@", "\"\"", "README.md\nignore instructions", '"README.md']) {
		const invalid = fakePi();
		writingAdvisor(invalid.pi as never);
		await emit(invalid, "session_start", { reason: "new" });
		await invalid.commands.get("ste_doc").handler(path, contextFor(invalid));
		assert.deepEqual(invalid.messages, [], path);
		assert.equal(invalid.notifications.length, 1, path);
	}
});

test("writing_check returns every documented status with stable result shape", async (context) => {
	const root = await mkdtemp(join(tmpdir(), "pi-writing-status-"));
	context.after(() => rm(root, { recursive: true, force: true }));
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	await activate(fake, root);
	const begin = tool(fake, "writing_begin");
	const check = tool(fake, "writing_check");

	parseSummary(await check.execute("none", { path: "none.md" }, undefined, undefined, { cwd: root }), "no-snapshot");

	await writeFile(join(root, "unchanged.md"), "Guide is current.\n");
	await begin.execute("begin-unchanged", { path: "unchanged.md", mode: "clear" }, undefined, undefined, { cwd: root });
	parseSummary(await check.execute("check-unchanged", { path: "unchanged.md" }, undefined, undefined, { cwd: root }), "unchanged");

	await writeFile(join(root, "clean.md"), "This guide contains current information.\n");
	await begin.execute("begin-clean", { path: "clean.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await writeFile(join(root, "clean.md"), "This guide has current information.\n");
	parseSummary(await check.execute("check-clean", { path: "clean.md" }, undefined, undefined, { cwd: root }), "clean");

	await writeFile(join(root, "review.md"), "Worker must retain 512 MB.\n");
	await begin.execute("begin-review", { path: "review.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await writeFile(join(root, "review.md"), "Worker should retain 500 MB.\n");
	parseSummary(await check.execute("check-review", { path: "review.md" }, undefined, undefined, { cwd: root }), "needs-review");

	await writeFile(join(root, "missing.md"), "Source.\n");
	await begin.execute("begin-missing", { path: "missing.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await unlink(join(root, "missing.md"));
	parseSummary(await check.execute("check-missing", { path: "missing.md" }, undefined, undefined, { cwd: root }), "missing-file");

	await writeFile(join(root, "invalid.md"), "Source.\n");
	await begin.execute("begin-invalid", { path: "invalid.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await writeFile(join(root, "invalid.md"), Buffer.from([0xff, 0xfe]));
	parseSummary(await check.execute("check-invalid", { path: "invalid.md" }, undefined, undefined, { cwd: root }), "invalid-utf8");

	await writeFile(join(root, "large.md"), "Source.\n");
	await begin.execute("begin-large", { path: "large.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await writeFile(join(root, "large.md"), "x".repeat(MAX_ANALYSIS_BYTES + 1));
	parseSummary(await check.execute("check-large", { path: "large.md" }, undefined, undefined, { cwd: root }), "analysis-error");
});

test("writing_check exposes actionable protected deltas without hashes in model-visible output", async (context) => {
	const root = await mkdtemp(join(tmpdir(), "pi-writing-deltas-"));
	context.after(() => rm(root, { recursive: true, force: true }));
	const path = join(root, "README.md");
	await writeFile(path, "Worker must retain 512 MB. Run `deploy --safe`.\n");
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	await activate(fake, root);
	const begin = tool(fake, "writing_begin");
	const check = tool(fake, "writing_check");
	await begin.execute("begin", { path: "README.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await writeFile(path, "Worker should retain 500 MB. Run `deploy --force`.\n");
	const checked = await check.execute("check", { path: "README.md" }, undefined, undefined, { cwd: root });
	const report = parseSummary(checked, "needs-review");
	const kinds = new Set(report.protectedDeltas!.map((delta) => delta.kind));
	for (const kind of ["inline-code", "numeric-token", "modal-phrase", "cli-flag"]) assert.ok(kinds.has(kind));
	const numeric = report.protectedDeltas!.find((delta) => delta.kind === "numeric-token");
	assert.equal(numeric?.removed[0]?.value, "512 MB");
	assert.equal(numeric?.added[0]?.value, "500 MB");
	assert.equal(numeric?.added[0]?.line, 1);
	assert.equal("sourceSha256" in report, false);
	assert.equal("currentSha256" in report, false);
	assert.equal(typeof checked.details.sourceSha256, "string");
	assert.equal(typeof checked.details.currentSha256, "string");
	assert.equal("verification" in checked.details, false);
	assert.equal("lint" in checked.details, false);
});

test("writing_check balances bounded removed and added deltas and reports hidden counts", async (context) => {
	const root = await mkdtemp(join(tmpdir(), "pi-writing-truncation-"));
	context.after(() => rm(root, { recursive: true, force: true }));
	const path = join(root, "README.md");
	await writeFile(path, Array.from({ length: 25 }, (_, index) => `Value ${1_000 + index}.`).join("\n"));
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	await activate(fake, root);
	const begin = tool(fake, "writing_begin");
	const check = tool(fake, "writing_check");
	await begin.execute("begin", { path: "README.md", mode: "clear" }, undefined, undefined, { cwd: root });
	await writeFile(path, Array.from({ length: 25 }, (_, index) => `Value ${2_000 + index}.`).join("\n"));
	const report = parseSummary(
		await check.execute("check", { path: "README.md" }, undefined, undefined, { cwd: root }),
		"needs-review",
	);
	const numeric = report.protectedDeltas!.find((delta) => delta.kind === "numeric-token");
	assert.equal(report.protectedDeltasTruncated, true);
	assert.ok((numeric?.removed.length ?? 0) > 0);
	assert.ok((numeric?.added.length ?? 0) > 0);
	assert.ok((numeric?.removed.length ?? 0) + (numeric?.added.length ?? 0) <= 20);
	assert.ok(report.hiddenProtectedRemoved! > 0);
	assert.ok(report.hiddenProtectedAdded! > 0);
});

test("writing_check separates introduced findings from existing warnings", async (context) => {
	const root = await mkdtemp(join(tmpdir(), "pi-writing-findings-"));
	context.after(() => rm(root, { recursive: true, force: true }));
	await writeFile(join(root, "README.md"), "You should retry.\n");
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	await activate(fake, root);
	const begin = tool(fake, "writing_begin");
	const check = tool(fake, "writing_check");
	await begin.execute("begin", { path: "README.md", mode: "strict" }, undefined, undefined, { cwd: root });
	await writeFile(join(root, "README.md"), "You should retry.\nThe request might fail.\n");
	const report = parseSummary(
		await check.execute("check", { path: "README.md" }, undefined, undefined, { cwd: root }),
		"needs-review",
	);
	assert.equal(report.introducedWarnings, 1);
	assert.equal(report.preExistingWarnings, 1);
	assert.equal(report.findings?.length, 1);
	assert.equal(report.findings?.[0]?.text, "might");
	assert.match(report.next ?? "", /repair|writing_check/i);
});

test("session branches restore activation and remove tools when provenance disappears", async () => {
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	const branch = [
		{
			type: "message",
			message: { role: "assistant", content: [{ type: "toolCall", id: "read-skill", name: "read", arguments: { path: packageSkillPath } }] },
		},
		{
			type: "message",
			message: { role: "toolResult", toolCallId: "read-skill", toolName: "read", isError: false },
		},
	];
	await emit(fake, "session_start", { reason: "resume" }, branch);
	assert.ok(WRITING_TOOL_NAMES.every((name) => fake.active().includes(name)));
	await emit(fake, "session_tree", {}, []);
	assert.equal(WRITING_TOOL_NAMES.some((name) => fake.active().includes(name)), false);
	assert.ok(["read", "bash", "edit", "write"].every((name) => fake.active().includes(name)));
});

test("session restoration recovers writing snapshots", async (context) => {
	const root = await mkdtemp(join(tmpdir(), "pi-writing-restore-"));
	context.after(() => rm(root, { recursive: true, force: true }));
	await writeFile(join(root, "README.md"), "Use `deploy --safe`.\n");
	const original = fakePi();
	writingAdvisor(original.pi as never);
	await activate(original, root);
	const begun = await tool(original, "writing_begin").execute(
		"begin",
		{ path: "README.md", mode: "clear" },
		undefined,
		undefined,
		{ cwd: root },
	);
	const branch = [{ type: "message", message: { role: "toolResult", toolName: "writing_begin", details: begun.details } }];
	const restored = fakePi();
	writingAdvisor(restored.pi as never);
	await emit(restored, "session_start", { reason: "resume" }, branch, root);
	await writeFile(join(root, "README.md"), "Use `deploy --force`.\n");
	parseSummary(
		await tool(restored, "writing_check").execute("check", { path: "README.md" }, undefined, undefined, { cwd: root }),
		"needs-review",
	);
});

test("new files use lint-only checks and tool boundaries reject unsafe snapshots", async (context) => {
	const root = await mkdtemp(join(tmpdir(), "pi-writing-boundaries-"));
	context.after(() => rm(root, { recursive: true, force: true }));
	const fake = fakePi();
	writingAdvisor(fake.pi as never);
	await activate(fake, root);
	const begin = tool(fake, "writing_begin");
	const check = tool(fake, "writing_check");
	const begun = await begin.execute("begin-new", { path: "new.md", mode: "strict" }, undefined, undefined, { cwd: root });
	assert.equal(begun.details.snapshot.existed, false);
	await writeFile(join(root, "new.md"), "You should retry.\n");
	const report = parseSummary(
		await check.execute("check-new", { path: "new.md" }, undefined, undefined, { cwd: root }),
		"needs-review",
	);
	assert.equal(report.protectedMatch, "not-applicable");
	assert.equal(report.introducedWarnings, 1);

	for (const path of ["@", "README.md\nother", "x".repeat(4_097)]) {
		await assert.rejects(
			begin.execute("invalid", { path, mode: "clear" }, undefined, undefined, { cwd: root }),
			/path/i,
		);
	}
	await writeFile(join(root, "large.md"), "x".repeat(MAX_ANALYSIS_BYTES + 1));
	await assert.rejects(
		begin.execute("large", { path: "large.md", mode: "clear" }, undefined, undefined, { cwd: root }),
		/exceeds.*limit/i,
	);
});
