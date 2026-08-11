import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skillPath = join(root, "skills", "clear-technical-writing", "SKILL.md");
const extensionPath = join(root, "extensions", "writing-advisor.ts");

function rpc(args: string[], input: object, env: NodeJS.ProcessEnv, timeoutMs = 15_000) {
	return new Promise<{ code: number | null; stdout: string; stderr: string }>((done, reject) => {
		const child = spawn("pi", args, { cwd: root, env, stdio: ["pipe", "pipe", "pipe"] });
		let stdout = "";
		let stderr = "";
		let settled = false;
		const timer = setTimeout(() => {
			if (settled) return;
			settled = true;
			child.kill("SIGKILL");
			reject(new Error(`Pi RPC timed out after ${timeoutMs} ms\nstdout:\n${stdout}\nstderr:\n${stderr}`));
		}, timeoutMs);
		child.stdout.on("data", (chunk) => { stdout += chunk; });
		child.stderr.on("data", (chunk) => { stderr += chunk; });
		child.on("error", (error) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			reject(error);
		});
		child.on("close", (code) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			done({ code, stdout, stderr });
		});
		child.stdin.end(`${JSON.stringify(input)}\n`);
	});
}

async function manifest() {
	return JSON.parse(await readFile(join(root, "package.json"), "utf8"));
}

test("package manifest points to loadable Pi resources", async () => {
	const value = await manifest();
	assert.deepEqual(value.pi.extensions, ["./extensions/writing-advisor.ts"]);
	assert.deepEqual(value.pi.skills, ["./skills"]);
	for (const path of value.pi.extensions) await readFile(resolve(root, path));
	await readFile(skillPath);
	for (const dependency of ["@earendil-works/pi-ai", "@earendil-works/pi-coding-agent", "typebox"]) {
		assert.equal(value.peerDependencies[dependency], "*");
	}
});

test("gallery metadata exposes package and skill names", async () => {
	const value = await manifest();
	assert.ok(value.keywords.includes("pi-package"));
	assert.ok(value.keywords.includes("clear-technical-writing"));
	assert.equal(typeof value.description, "string");
	assert.ok(value.description.length > 20);
});

test("skill references resolve from skill root", async () => {
	const skill = await readFile(skillPath, "utf8");
	const references = [...skill.matchAll(/`(references\/[^`]+\.md)`/g)].map((match) => match[1]!);
	assert.ok(references.length > 0);
	for (const relative of new Set(references)) await readFile(resolve(dirname(skillPath), relative));
});

test("release workflow checks tagged source before publishing configured npm tag", async () => {
	const value = await manifest();
	const workflow = await readFile(join(root, ".github", "workflows", "publish.yml"), "utf8");
	const install = workflow.indexOf("npm ci");
	const check = workflow.indexOf("npm run check");
	const publish = workflow.indexOf("npm publish");
	assert.ok(install >= 0 && install < check && check < publish);
	const tag = /npm publish[^\n]*--tag\s+(\S+)/.exec(workflow)?.[1];
	assert.equal(tag, value.publishConfig.tag);
});

test("npm package contains declared runtime resources", async () => {
	const { execFile } = await import("node:child_process");
	const { promisify } = await import("node:util");
	const { stdout } = await promisify(execFile)("npm", ["pack", "--dry-run", "--json"], { cwd: root });
	const payload = JSON.parse(stdout);
	const packed = Array.isArray(payload) ? payload[0] : Object.values(payload)[0];
	const paths = new Set<string>(((packed as any).files as any[]).map((entry) => String(entry.path)));
	const value = await manifest();
	for (const extension of value.pi.extensions) assert.ok(paths.has(extension.replace(/^\.\//, "")));
	assert.ok(paths.has("skills/clear-technical-writing/SKILL.md"));
	assert.ok([...paths].some((path) => path.startsWith("skills/clear-technical-writing/references/")));
	assert.deepEqual((packed as any).bundled ?? [], []);
});

test("isolated Pi discovery exposes one package skill and one package command", async (context) => {
	const agentDir = await mkdtemp(join(tmpdir(), "pi-writing-discovery-"));
	context.after(() => rm(agentDir, { recursive: true, force: true }));
	const result = await rpc([
		"--mode", "rpc",
		"--no-session",
		"--no-extensions",
		"--no-skills",
		"--no-prompt-templates",
		"--no-themes",
		"--no-context-files",
		"--no-approve",
		"--offline",
		"-e", root,
	], { id: "commands", type: "get_commands" }, {
		...process.env,
		PI_CODING_AGENT_DIR: agentDir,
		PI_TELEMETRY: "0",
		PI_SKIP_VERSION_CHECK: "1",
	});
	assert.equal(result.code, 0, result.stderr);
	const records = result.stdout.split("\n").filter(Boolean).map((line) => JSON.parse(line));
	const response = records.find((item) => item.type === "response" && item.id === "commands");
	assert.equal(response?.success, true, result.stdout);
	const commands = response.data.commands;
	const packageCommands = commands.filter((item: any) =>
		item.source === "extension" && resolve(item.sourceInfo.path) === resolve(extensionPath)
	);
	assert.deepEqual(packageCommands.map((item: any) => item.name), ["ste_doc"]);
	const skills = commands.filter((item: any) => item.name === "skill:clear-technical-writing");
	assert.equal(skills.length, 1);
	assert.equal(resolve(skills[0].sourceInfo.path), resolve(skillPath));
});
