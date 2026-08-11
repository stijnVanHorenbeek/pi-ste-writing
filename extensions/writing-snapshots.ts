import { createHash, randomUUID } from "node:crypto";
import { readFile, realpath } from "node:fs/promises";
import { basename, dirname, isAbsolute, join, resolve } from "node:path";

import { MAX_ANALYSIS_BYTES, type WritingMode } from "./writing-analysis.ts";

export const SNAPSHOT_VERSION = 1;
export const MAX_WRITING_PATH_CHARS = 4_096;

export interface WritingSnapshot {
	version: 1;
	snapshotId: string;
	path: string;
	displayPath: string;
	mode: WritingMode;
	existed: boolean;
	sha256?: string;
	sourceText?: string;
}

export interface ReadTextResult {
	path: string;
	bytes: Buffer;
	text: string;
	sha256: string;
}

function normalizeInputPath(path: string): string {
	const value = path.startsWith("@") ? path.slice(1) : path;
	if (!value) throw new Error("Writing path must not be empty");
	if (value.length > MAX_WRITING_PATH_CHARS) {
		throw new Error(`Writing path exceeds ${MAX_WRITING_PATH_CHARS}-character limit`);
	}
	if (/[\u0000-\u001F\u007F]/u.test(value)) throw new Error("Writing path contains a control character");
	return value;
}

export async function canonicalPath(path: string, cwd: string): Promise<string> {
	const normalized = normalizeInputPath(path);
	const absolute = isAbsolute(normalized) ? resolve(normalized) : resolve(cwd, normalized);
	let ancestor = absolute;
	const missingSegments: string[] = [];
	while (true) {
		try {
			return join(await realpath(ancestor), ...missingSegments);
		} catch (error) {
			if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
			const parent = dirname(ancestor);
			if (parent === ancestor) return absolute;
			missingSegments.unshift(basename(ancestor));
			ancestor = parent;
		}
	}
}

export async function readUtf8(path: string, cwd: string): Promise<ReadTextResult> {
	const resolved = await canonicalPath(path, cwd);
	const bytes = await readFile(resolved);
	if (bytes.byteLength > MAX_ANALYSIS_BYTES) {
		throw new RangeError(`Writing file exceeds ${MAX_ANALYSIS_BYTES}-byte analysis limit: ${path}`);
	}
	let text: string;
	try {
		text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
	} catch {
		throw new Error(`Writing analysis requires UTF-8 text: ${path}`);
	}
	return {
		path: resolved,
		bytes,
		text,
		sha256: createHash("sha256").update(bytes).digest("hex"),
	};
}

export async function captureSnapshot(
	path: string,
	mode: WritingMode,
	cwd: string,
): Promise<WritingSnapshot> {
	const displayPath = normalizeInputPath(path);
	try {
		const source = await readUtf8(displayPath, cwd);
		return {
			version: SNAPSHOT_VERSION,
			snapshotId: randomUUID(),
			path: source.path,
			displayPath,
			mode,
			existed: true,
			sha256: source.sha256,
			sourceText: source.text,
		};
	} catch (error) {
		if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
		return {
			version: SNAPSHOT_VERSION,
			snapshotId: randomUUID(),
			path: await canonicalPath(displayPath, cwd),
			displayPath,
			mode,
			existed: false,
		};
	}
}

export function isWritingSnapshot(value: unknown): value is WritingSnapshot {
	if (typeof value !== "object" || value === null) return false;
	const snapshot = value as Partial<WritingSnapshot>;
	if (
		snapshot.version !== SNAPSHOT_VERSION
		|| typeof snapshot.snapshotId !== "string"
		|| typeof snapshot.path !== "string"
		|| typeof snapshot.displayPath !== "string"
		|| !["clear", "procedure", "strict"].includes(snapshot.mode ?? "")
		|| typeof snapshot.existed !== "boolean"
	) return false;
	if (!snapshot.existed) return snapshot.sha256 === undefined && snapshot.sourceText === undefined;
	return typeof snapshot.sha256 === "string" && typeof snapshot.sourceText === "string";
}

export function restoreSnapshots(branch: any[]): Map<string, WritingSnapshot> {
	const snapshots = new Map<string, WritingSnapshot>();
	for (const entry of branch) {
		const message = entry?.type === "message" ? entry.message : undefined;
		if (message?.role !== "toolResult" || message.toolName !== "writing_begin") continue;
		const snapshot = message.details?.snapshot;
		if (isWritingSnapshot(snapshot)) snapshots.set(snapshot.path, snapshot);
	}
	return snapshots;
}
