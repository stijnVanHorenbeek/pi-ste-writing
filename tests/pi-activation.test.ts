import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

import {
	createAgentSession,
	DefaultResourceLoader,
	SessionManager,
	SettingsManager,
} from "@earendil-works/pi-coding-agent";

import { packageSkillPath, WRITING_TOOL_NAMES } from "../extensions/writing-advisor.ts";

const extensionPath = resolve("extensions/writing-advisor.ts");

test("real Pi SDK activates writing tools on exact package skill invocation", async (context) => {
	const agentDir = await mkdtemp(join(tmpdir(), "pi-writing-sdk-"));
	context.after(() => rm(agentDir, { recursive: true, force: true }));
	const stopperPath = join(agentDir, "stop-after-input.ts");
	await writeFile(stopperPath, 'export default (pi: any) => pi.on("input", () => ({ action: "handled" }));\n');
	const settingsManager = SettingsManager.inMemory();
	const loader = new DefaultResourceLoader({
		cwd: process.cwd(),
		agentDir,
		settingsManager,
		additionalExtensionPaths: [extensionPath, stopperPath],
		additionalSkillPaths: [packageSkillPath],
		skillsOverride: (result) => ({
			...result,
			skills: result.skills.filter((skill) => resolve(skill.filePath) === resolve(packageSkillPath)),
		}),
		systemPromptOverride: () => "Follow loaded skills.",
	});
	await loader.reload();
	assert.deepEqual(loader.getExtensions().errors, []);
	assert.ok(loader.getExtensions().extensions.some((extension) => resolve(extension.path) === extensionPath));
	assert.deepEqual(loader.getSkills().skills.map((skill) => resolve(skill.filePath)), [resolve(packageSkillPath)]);

	const { session } = await createAgentSession({
		cwd: process.cwd(),
		agentDir,
		settingsManager,
		resourceLoader: loader,
		sessionManager: SessionManager.inMemory(),
	});
	context.after(() => session.dispose());
	const ambient = session.getActiveToolNames();
	assert.equal(WRITING_TOOL_NAMES.some((name) => ambient.includes(name)), false);

	await session.prompt("/skill:clear-technical-writing improve README");
	assert.deepEqual(
		new Set(session.getActiveToolNames()),
		new Set([...ambient, ...WRITING_TOOL_NAMES]),
	);
});
