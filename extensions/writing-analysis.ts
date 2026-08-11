/*
 * Heuristic technical-writing analysis.
 *
 * Ported from this package's Python implementation, adapted from
 * AminBlg/SimpleEnglish at commit 59bf6702197a5aadc96d197ea17f290d8d50dcd3.
 * Copyright (c) 2026 AminBlg. MIT licensed; see repository LICENSE.
 */

export type WritingMode = "clear" | "procedure" | "strict";

export const LINT_DISCLAIMER = "Advisory only; does not certify ASD-STE100 compliance.";
export const VERIFIER_DISCLAIMER =
	"Mechanical protected-content verification only; does not prove semantic equivalence or ASD-STE100 compliance.";
export const MAX_ANALYSIS_BYTES = 2 * 1024 * 1024;
const MAX_REGEX_MATCHES = 100_000;

function assertAnalysisSize(...values: string[]) {
	for (const value of values) {
		if (Buffer.byteLength(value, "utf8") > MAX_ANALYSIS_BYTES) {
			throw new RangeError(`Analysis input exceeds ${MAX_ANALYSIS_BYTES}-byte limit`);
		}
	}
}

function normalizeCodeValue(value: string): string {
	return value.replace(/\r\n?/g, "\n");
}

interface MatchSpan {
	start: number;
	end: number;
}

interface ValueSpan extends MatchSpan {
	valueStart: number;
	value: string;
}

interface Occurrence {
	value: string;
	offset: number;
}

export interface ProtectedEntry {
	value: string;
	container: string;
	offset: number;
}

export interface ProtectedViolation {
	rule: "protected-occurrence";
	kind: string;
	expected: ProtectedEntry[];
	actual: ProtectedEntry[];
}

export interface VerificationReport {
	ok: boolean;
	violations: ProtectedViolation[];
	disclaimer: string;
}

export interface LintFinding {
	rule: string;
	category: "semantic" | "style" | "procedure";
	severity: "warning";
	source: string;
	line: number;
	column: number;
	text: string;
	message: string;
	protected_kind?: string;
}

export interface LintReport {
	advisory: true;
	mode: WritingMode;
	findings: LintFinding[];
	summary: { warnings: number };
	disclaimer: string;
}

const INLINE_CODE_RE = /(?<!`)(?<ticks>`+)(?!`)(?<value>[^\n]*?)\k<ticks>(?!`)/g;
const FENCE_OPEN_RE = /^(?<indent>[ \t]{0,3})(?<marker>`{3,}|~{3,})[^\n]*(?:\n|$)/gm;
const INDENTED_CODE_RE = /(?:^(?: {4}|\t)[^\n]*(?:\n|$))+/gm;
const LINK_OPEN_RE = /\[[^\]\n]*\]\(/g;
const DIAGNOSTIC_RE = /^>\s*(?:Error|Log|Test):[^\n]*$/gim;
const URL_RE = /https?:\/\/[^\s)>]+/g;
const NUMBER_RE = /(?<![\p{L}\p{N}_.])(?:\p{Nd}{1,2}:\p{Nd}{2}(?::\p{Nd}{2})?|v?\p{Nd}[\p{Nd},]*(?:\.\p{Nd}+)*(?:-\p{Nd}[\p{Nd},]*(?:\.\p{Nd}+)*)*%?(?:\s*(?:ms|seconds?|minutes?|hours?|days?|MB|GB|TB))?)/giu;
const PATH_RE = /(?<![\p{L}\p{N}_])(?:\/|\.{1,2}\/)[A-Za-z0-9._~${}-]+(?:\/[A-Za-z0-9._~${}-]+)*|\b[A-Za-z]:\\[^\s`"']+/gu;
const CONTRACTION_RE = /(?<![\p{L}\p{N}_])(?:[\p{L}\p{N}_]+n't|(?:I|you|we|they|he|she|it|that|there|here|what|who|where|when|why|how)'(?:ll|re|ve|d|s))(?![\p{L}\p{N}_])/giu;
const LATIN_RE = /(?<![\p{L}\p{N}_])(?:e\.g\.|i\.e\.|etc\.?)(?![\p{L}\p{N}_])/giu;
const MODAL_RE = /(?<![\p{L}\p{N}_])(should|may|might|could)(?![\p{L}\p{N}_])/giu;
const MODAL_PHRASE_RE = /(?<![\p{L}\p{N}_])(?:must(?:\s+not)?|should(?:\s+not)?|can(?:not|\s+not)?|may(?:\s+not)?|might(?:\s+not)?|could(?:\s+not)?)(?![\p{L}\p{N}_])/giu;
const CLI_FLAG_RE = /(?<![\p{L}\p{N}_-])--[A-Za-z0-9][A-Za-z0-9-]*(?:=[^\s`]+)?/gu;
const ENVIRONMENT_VARIABLE_RE = /(?<![\p{L}\p{N}_])(?:\$\{[A-Za-z_][A-Za-z0-9_]*\}|\$[A-Za-z_][A-Za-z0-9_]*)/gu;
const LINK_LABEL_RE = /\[([^\]\n]*)\]\(/g;
const BOLD_TEXT_RE = /(?<!\*)\*\*(?!\*)([^\n]+?)(?<!\*)\*\*(?!\*)|(?<!_)__(?!_)([^\n]+?)(?<!_)__(?!_)/g;
const JSON_KEY_RE = /"((?:\\.|[^"\\])*)"\s*:/g;
const IDENTIFIER_RE = /(?<![\p{L}\p{N}_])(?:[A-Z]{2,}[A-Z0-9_-]*|[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+)(?![\p{L}\p{N}_])/gu;
const MODAL_IDENTIFIER_WORDS = new Set(["must", "not", "should", "can", "cannot", "may", "might", "could"]);

const IMPERATIVE_VERBS = new Set([
	"add", "apply", "call", "check", "choose", "click", "copy", "configure", "confirm",
	"contact", "create", "delete", "download", "edit", "ensure", "enter", "execute",
	"install", "make", "open", "press", "read", "remove", "replace", "restore", "restart",
	"retry", "run", "save", "select", "set", "start", "stop", "update", "upload", "use",
	"verify", "wait", "write",
]);

function matches(regex: RegExp, text: string): RegExpExecArray[] {
	const flags = regex.flags.includes("g") ? regex.flags : `${regex.flags}g`;
	const copy = new RegExp(regex.source, flags);
	const result: RegExpExecArray[] = [];
	for (const match of text.matchAll(copy)) {
		if (result.length >= MAX_REGEX_MATCHES) {
			throw new RangeError(`Analysis regex work limit exceeded (${MAX_REGEX_MATCHES} matches)`);
		}
		result.push(match);
	}
	return result;
}

function ranges(regex: RegExp, text: string): MatchSpan[] {
	return matches(regex, text).map((match) => ({ start: match.index, end: match.index + match[0].length }));
}

function maskRange(characters: string[], start: number, end: number) {
	for (let index = start; index < end; index += 1) {
		if (characters[index] !== "\n") characters[index] = " ";
	}
}

function rangeResolver(candidates: MatchSpan[]): (offset: number) => boolean {
	const sorted = [...candidates].sort((left, right) => left.start - right.start || left.end - right.end);
	const merged: MatchSpan[] = [];
	for (const candidate of sorted) {
		const previous = merged.at(-1);
		if (previous && candidate.start <= previous.end) previous.end = Math.max(previous.end, candidate.end);
		else merged.push({ ...candidate });
	}
	return (offset: number) => {
		let low = 0;
		let high = merged.length - 1;
		while (low <= high) {
			const middle = Math.floor((low + high) / 2);
			const range = merged[middle]!;
			if (offset < range.start) high = middle - 1;
			else if (offset >= range.end) low = middle + 1;
			else return true;
		}
		return false;
	};
}

function escapeRegex(value: string): string {
	return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function fencedCodeSpans(text: string): ValueSpan[] {
	const spans: ValueSpan[] = [];
	const openerRegex = new RegExp(FENCE_OPEN_RE.source, FENCE_OPEN_RE.flags);
	let position = 0;
	while (position <= text.length) {
		openerRegex.lastIndex = position;
		const opener = openerRegex.exec(text);
		if (!opener) break;
		const marker = opener.groups?.marker ?? "```";
		const indent = opener.groups?.indent ?? "";
		const closerRegex = new RegExp(
			`^[ \\t]{0,3}${escapeRegex(marker[0] ?? "`")}{${marker.length},}[ \\t]*(?:\\r?\\n|$)`,
			"gm",
		);
		closerRegex.lastIndex = opener.index + opener[0].length;
		const closer = closerRegex.exec(text);
		const valueStart = opener.index + opener[0].length;
		const end = closer ? closer.index + closer[0].length : text.length;
		const rawValue = text.slice(valueStart, closer?.index ?? text.length);
		const value = normalizeCodeValue(indent
			? rawValue.replace(new RegExp(`^${escapeRegex(indent)}`, "gm"), "")
			: rawValue);
		spans.push({ start: opener.index, end, valueStart, value });
		if (!closer) break;
		position = end;
	}
	return spans;
}

export function linkDestinationSpans(text: string): ValueSpan[] {
	const closers = new Map<number, number>();
	const stack: number[] = [];
	for (let index = 0; index < text.length; index += 1) {
		const character = text[index];
		if (character === "\\" && index + 1 < text.length) {
			index += 1;
			continue;
		}
		if (character === "\n") {
			stack.length = 0;
			continue;
		}
		if (character === "(") stack.push(index);
		else if (character === ")") {
			const opener = stack.pop();
			if (opener !== undefined) closers.set(opener, index);
		}
	}

	const spans: ValueSpan[] = [];
	for (const opener of matches(LINK_OPEN_RE, text)) {
		const openingParenthesis = opener.index + opener[0].length - 1;
		const close = closers.get(openingParenthesis);
		if (close === undefined) continue;
		const start = openingParenthesis + 1;
		spans.push({
			start: opener.index,
			end: close + 1,
			valueStart: start,
			value: text.slice(start, close),
		});
	}
	return spans;
}

function maskMarkdown(text: string): string {
	const characters = text.split("");
	for (const span of fencedCodeSpans(text)) maskRange(characters, span.start, span.end);
	const frontmatter = /^---\s*\n[\s\S]*?^---\s*$/m.exec(text);
	if (frontmatter?.index === 0) maskRange(characters, 0, frontmatter[0].length);
	for (const regex of [INDENTED_CODE_RE, INLINE_CODE_RE, DIAGNOSTIC_RE, URL_RE]) {
		for (const span of ranges(regex, text)) maskRange(characters, span.start, span.end);
	}
	for (const span of linkDestinationSpans(text)) maskRange(characters, span.valueStart, span.end - 1);
	return characters.join("");
}

function maskHeadings(text: string): string {
	const characters = text.split("");
	for (const span of ranges(/^#{1,6}\s+[^\n]*$/gm, text)) maskRange(characters, span.start, span.end);
	return characters.join("");
}

function sentenceSpans(text: string): MatchSpan[] {
	const boundary = text.split("");
	for (let index = 1; index < boundary.length - 1; index += 1) {
		if (boundary[index] === "." && /\p{Nd}/u.test(boundary[index - 1] ?? "") && /\p{Nd}/u.test(boundary[index + 1] ?? "")) {
			boundary[index] = "·";
		}
	}
	for (const match of matches(LATIN_RE, text)) {
		for (let index = match.index; index < match.index + match[0].length; index += 1) {
			if (boundary[index] === ".") boundary[index] = "·";
		}
	}

	const spans: MatchSpan[] = [];
	let start = 0;
	for (let index = 0; index < boundary.length; index += 1) {
		if (!".!?".includes(boundary[index] ?? "")) continue;
		let end = index + 1;
		while (end < boundary.length && /["'”’\)\]}*_]/.test(boundary[end] ?? "")) end += 1;
		if (end < boundary.length && !/\s/.test(boundary[end] ?? "")) continue;
		const segment = text.slice(start, end);
		const leading = segment.length - segment.trimStart().length;
		if (text.slice(start + leading, end).trim()) spans.push({ start: start + leading, end });
		start = end;
	}
	const tail = text.slice(start);
	const leading = tail.length - tail.trimStart().length;
	if (text.slice(start + leading).trim()) spans.push({ start: start + leading, end: text.length });
	return spans;
}

function isInstruction(sentence: string): boolean {
	const candidate = sentence.trim().replace(/^(?:#+\s+|[-*]\s+|\d+\.\s+)/, "");
	const first = /^([A-Za-z]+)\b/.exec(candidate)?.[1]?.toLowerCase();
	return first !== undefined && IMPERATIVE_VERBS.has(first);
}

export function protectedSpans(text: string): Record<string, Occurrence[]> {
	const fenced = fencedCodeSpans(text);
	const fencedRanges = fenced.map(({ start, end }) => ({ start, end }));
	const inFencedCode = rangeResolver(fencedRanges);
	const indented = matches(INDENTED_CODE_RE, text).filter((match) => !inFencedCode(match.index));
	const codeRanges = [
		...fencedRanges,
		...indented.map((match) => ({ start: match.index, end: match.index + match[0].length })),
	];
	const inCode = rangeResolver(codeRanges);
	const inline = matches(INLINE_CODE_RE, text).filter((match) => !inCode(match.index));
	const links = linkDestinationSpans(text);
	const diagnostics = matches(DIAGNOSTIC_RE, text);
	const urls = matches(URL_RE, text);
	const urlRanges = urls.map((match) => ({ start: match.index, end: match.index + match[0].length }));
	const nonBareUrlRanges = [
		...codeRanges,
		...inline.map((match) => ({ start: match.index, end: match.index + match[0].length })),
		...links.map(({ start, end }) => ({ start, end })),
		...diagnostics.map((match) => ({ start: match.index, end: match.index + match[0].length })),
	];
	const inNonBareUrl = rangeResolver(nonBareUrlRanges);
	const inUrl = rangeResolver(urlRanges);
	const fencedValues: Occurrence[] = fenced.map((span) => ({ value: span.value, offset: span.valueStart }));
	for (const match of indented) {
		const value = normalizeCodeValue(match[0]
			.split(/(?<=\n)/)
			.map((line) => line.startsWith("    ") ? line.slice(4) : line.slice(1))
			.join(""));
		fencedValues.push({ value, offset: match.index + (match[0].startsWith("    ") ? 4 : 1) });
	}
	return {
		"inline-code": inline.map((match) => {
			const value = match.groups?.value ?? "";
			return { value, offset: match.index + match[0].indexOf(value) };
		}),
		"fenced-code": fencedValues,
		"link-destination": links.map((span) => ({ value: span.value, offset: span.valueStart })),
		"quoted-diagnostic": diagnostics.map((match) => ({ value: match[0].trim(), offset: match.index })),
		"bare-url": urls
			.filter((match) => !inNonBareUrl(match.index))
			.map((match) => ({ value: match[0], offset: match.index })),
		"numeric-token": matches(NUMBER_RE, text).map((match) => ({ value: match[0], offset: match.index })),
		"modal-phrase": matches(MODAL_PHRASE_RE, text)
			.filter((match) => !inNonBareUrl(match.index))
			.map((match) => ({ value: match[0].replace(/\s+/g, " "), offset: match.index })),
		"path": matches(PATH_RE, text)
			.filter((match) => !inUrl(match.index))
			.map((match) => ({ value: match[0], offset: match.index })),
	};
}

function occurrenceCounter(occurrences: Occurrence[]): Map<string, number> {
	const counter = new Map<string, number>();
	for (const { value } of occurrences) counter.set(value, (counter.get(value) ?? 0) + 1);
	return counter;
}

function countersEqual(left: Map<string, number>, right: Map<string, number>): boolean {
	if (left.size !== right.size) return false;
	for (const [key, value] of left) if (right.get(key) !== value) return false;
	return true;
}

function changedSpan(expected: Occurrence[], actual: Occurrence[]): Occurrence {
	const remaining = occurrenceCounter(expected);
	for (const occurrence of actual) {
		const count = remaining.get(occurrence.value) ?? 0;
		if (count > 0) remaining.set(occurrence.value, count - 1);
		else return occurrence;
	}
	const expectedCounter = occurrenceCounter(expected);
	const actualCounter = occurrenceCounter(actual);
	for (const { value } of expected) {
		if ((expectedCounter.get(value) ?? 0) > (actualCounter.get(value) ?? 0)) {
			return { value: `missing ${value}`, offset: 0 };
		}
	}
	return { value: "missing protected value", offset: 0 };
}

export function textLocation(text: string, offset: number): { line: number; column: number } {
	const before = text.slice(0, offset);
	const line = before.split("\n").length;
	const lineStart = before.lastIndexOf("\n") + 1;
	const column = [...text.slice(lineStart, offset)].length + 1;
	return { line, column };
}

function makeFinding(
	rule: string,
	category: LintFinding["category"],
	source: string,
	text: string,
	offset: number,
	offendingText: string,
	message: string,
	extra: Partial<LintFinding> = {},
): LintFinding {
	return {
		rule,
		category,
		severity: "warning",
		source,
		...textLocation(text, offset),
		text: offendingText,
		message,
		...extra,
	};
}

export function lintText(
	text: string,
	mode: WritingMode,
	source: string,
	sourceText?: string,
): LintReport {
	assertAnalysisSize(text, ...(sourceText === undefined ? [] : [sourceText]));
	const findings: LintFinding[] = [];
	const analysisText = maskMarkdown(text);
	if (sourceText !== undefined) {
		const expected = protectedSpans(sourceText);
		const actual = protectedSpans(text);
		for (const kind of Object.keys(expected)) {
			if (countersEqual(occurrenceCounter(expected[kind] ?? []), occurrenceCounter(actual[kind] ?? []))) continue;
			const changed = changedSpan(expected[kind] ?? [], actual[kind] ?? []);
			findings.push(makeFinding(
				"protected-span",
				"semantic",
				source,
				text,
				changed.offset,
				changed.value,
				`Protected ${kind} values differ from source.`,
				{ protected_kind: kind },
			));
		}
	}
	if (mode === "strict") {
		for (const match of matches(MODAL_RE, analysisText)) {
			const modal = match[0];
			findings.push(makeFinding(
				"modal", "semantic", source, text, match.index, modal,
				`Review modal "${modal}"; preserve its meaning. Strict STE may require a different construction.`,
			));
		}
		for (const match of matches(CONTRACTION_RE, analysisText)) {
			findings.push(makeFinding(
				"contraction", "style", source, text, match.index, text.slice(match.index, match.index + match[0].length),
				"Avoid contractions in strict STE; preserve the original meaning.",
			));
		}
		for (const match of matches(LATIN_RE, analysisText)) {
			findings.push(makeFinding(
				"latin-abbreviation", "style", source, text, match.index, text.slice(match.index, match.index + match[0].length),
				"Avoid Latin abbreviations in strict STE.",
			));
		}
	}

	const sentenceText = maskHeadings(analysisText);
	const spans = sentenceSpans(sentenceText);
	if (mode === "procedure" || mode === "strict") {
		for (const { start, end } of spans) {
			const sentence = sentenceText.slice(start, end);
			const instruction = isInstruction(sentence);
			if (mode === "procedure" && !instruction) continue;
			const limit = instruction ? 20 : 25;
			const wordCount = sentence.trim().split(/\s+/).filter(Boolean).length;
			if (wordCount <= limit) continue;
			findings.push(makeFinding(
				"sentence-length", "style", source, text, start, text.slice(start, end).trim(),
				`Sentence has ${wordCount} words; ${mode} mode limit is ${limit}.`,
			));
		}
	}
	if (mode === "procedure") {
		for (const { start, end } of spans) {
			const sentence = sentenceText.slice(start, end).trim();
			if (!isInstruction(sentence) || !/(?<![\p{L}\p{N}_])(if|when)(?![\p{L}\p{N}_])/iu.test(sentence)) continue;
			findings.push(makeFinding(
				"condition-order", "procedure", source, text, start, text.slice(start, end).trim(),
				"Put the action-controlling condition before the instruction.",
			));
		}
	}
	findings.sort((left, right) =>
		left.line - right.line
		|| left.column - right.column
		|| (left.rule < right.rule ? -1 : left.rule > right.rule ? 1 : 0)
	);
	return {
		advisory: true,
		mode,
		findings,
		summary: { warnings: findings.length },
		disclaimer: LINT_DISCLAIMER,
	};
}

interface LineIndex {
	containerAt(offset: number): string;
	onlyWhitespaceBefore(offset: number): boolean;
}

function createLineIndex(text: string): LineIndex {
	const starts: number[] = [];
	const firstContent: number[] = [];
	const containers: string[] = [];
	let start = 0;
	while (start <= text.length) {
		const newline = text.indexOf("\n", start);
		const end = newline < 0 ? text.length : newline;
		const line = text.slice(start, end);
		const stripped = line.trimStart();
		const heading = /^(#{1,6})\s+/.exec(stripped);
		starts.push(start);
		firstContent.push(start + line.length - stripped.length);
		containers.push(
			heading ? `heading-${heading[1]?.length ?? 1}`
				: stripped.startsWith(">") ? "blockquote"
					: "flow",
		);
		if (newline < 0) break;
		start = newline + 1;
	}
	const lineAt = (offset: number) => {
		let low = 0;
		let high = starts.length - 1;
		while (low < high) {
			const middle = Math.ceil((low + high) / 2);
			if ((starts[middle] ?? 0) <= offset) low = middle;
			else high = middle - 1;
		}
		return low;
	};
	return {
		containerAt: (offset) => containers[lineAt(offset)] ?? "flow",
		onlyWhitespaceBefore: (offset) => (firstContent[lineAt(offset)] ?? offset) >= offset,
	};
}

function isOrderedListMarker(
	text: string,
	value: string,
	offset: number,
	lines: LineIndex,
): boolean {
	return /^[.)]\s+/.test(text.slice(offset + value.length)) && lines.onlyWhitespaceBefore(offset);
}

function groupOccurrence(match: RegExpExecArray, group: string): Occurrence {
	const relative = match[0].indexOf(group);
	return { value: group, offset: match.index + Math.max(relative, 0) };
}

export function protectedInventory(text: string): Record<string, ProtectedEntry[]> {
	const occurrences = protectedSpans(text);
	const lines = createLineIndex(text);
	occurrences["numeric-token"] = (occurrences["numeric-token"] ?? [])
		.filter(({ value, offset }) => !isOrderedListMarker(text, value, offset, lines))
		.map(({ value, offset }) => ({ value: value.replace(/,+$/, ""), offset }));
	const cliFlags = matches(CLI_FLAG_RE, text);
	const environments = matches(ENVIRONMENT_VARIABLE_RE, text);
	occurrences["cli-flag"] = cliFlags.map((match) => ({ value: match[0], offset: match.index }));
	occurrences["environment-variable"] = environments.map((match) => ({ value: match[0], offset: match.index }));
	occurrences["link-label"] = matches(LINK_LABEL_RE, text).map((match) => groupOccurrence(match, match[1] ?? ""));
	occurrences["bold-text"] = matches(BOLD_TEXT_RE, text).map((match) => groupOccurrence(match, match[1] ?? match[2] ?? ""));
	occurrences["json-key"] = matches(JSON_KEY_RE, text).map((match) => groupOccurrence(match, match[1] ?? ""));
	const environmentRanges = environments.map((match) => ({ start: match.index, end: match.index + match[0].length }));
	const inEnvironment = rangeResolver(environmentRanges);
	occurrences.identifier = matches(IDENTIFIER_RE, text)
		.filter((match) => !inEnvironment(match.index))
		.filter((match) => !MODAL_IDENTIFIER_WORDS.has(match[0].toLowerCase()))
		.map((match) => ({ value: match[0], offset: match.index }));
	return Object.fromEntries(Object.entries(occurrences).map(([kind, values]) => [
		kind,
		values.map(({ value, offset }) => ({ value, container: lines.containerAt(offset), offset })),
	]));
}

function inventoryCounter(entries: ProtectedEntry[]): Map<string, number> {
	const counter = new Map<string, number>();
	for (const entry of entries) {
		const key = JSON.stringify([entry.value, entry.container]);
		counter.set(key, (counter.get(key) ?? 0) + 1);
	}
	return counter;
}

export function verifyProtectedContent(source: string, draft: string): VerificationReport {
	assertAnalysisSize(source, draft);
	const expected = protectedInventory(source);
	const actual = protectedInventory(draft);
	const violations: ProtectedViolation[] = [];
	for (const kind of Object.keys(expected)) {
		if (countersEqual(inventoryCounter(expected[kind] ?? []), inventoryCounter(actual[kind] ?? []))) continue;
		violations.push({
			rule: "protected-occurrence",
			kind,
			expected: expected[kind] ?? [],
			actual: actual[kind] ?? [],
		});
	}
	return { ok: violations.length === 0, violations, disclaimer: VERIFIER_DISCLAIMER };
}
