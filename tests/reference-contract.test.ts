import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";

const rulesPath = resolve("skills/clear-technical-writing/references/ste-rules.md");

test("strict reference retains complete rule and recommendation catalogs", async () => {
	const text = await readFile(rulesPath, "utf8");
	const expected = new Set([
		...Array.from({ length: 14 }, (_, index) => `1.${index + 1}`),
		...Array.from({ length: 2 }, (_, index) => `2.${index + 1}`),
		...Array.from({ length: 7 }, (_, index) => `3.${index + 1}`),
		...Array.from({ length: 5 }, (_, index) => `4.${index + 1}`),
		...Array.from({ length: 5 }, (_, index) => `5.${index + 1}`),
		...Array.from({ length: 6 }, (_, index) => `6.${index + 1}`),
		...Array.from({ length: 3 }, (_, index) => `7.${index + 1}`),
		...Array.from({ length: 7 }, (_, index) => `8.${index + 1}`),
		...Array.from({ length: 4 }, (_, index) => `9.${index + 1}`),
		...Array.from({ length: 8 }, (_, index) => `GR-${index + 1}`),
	]);
	const ids = [...text.matchAll(/^\|\s*((?:\d+\.\d+)|(?:GR-\d+))\s*\|/gm)].map((match) => match[1]!);
	assert.deepEqual(new Set(ids), expected);
	assert.equal(ids.length, expected.size);
});
