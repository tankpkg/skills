// Prompt Pack schema and loader for content-driven party games.
// A "prompt pack" is a JSON file containing questions, prompts, or challenges
// that the game engine draws from. This schema supports categories, difficulty,
// family-mode filtering, and localization.
//
// File format: /content/packs/{pack-id}.json
// Validate at build time: npx tsx prompt-pack.schema.ts --validate ./content/packs/*.json

import { readFileSync, readdirSync } from "fs";
import { join } from "path";

export interface Prompt {
  id: string;
  text: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  familySafe: boolean;
  locale: string;
  tags?: string[];
}

export interface PromptPack {
  id: string;
  name: string;
  version: number;
  locale: string;
  categories: string[];
  prompts: Prompt[];
}

// Validation

interface ValidationError {
  packId: string;
  promptId?: string;
  message: string;
}

export function validatePack(pack: PromptPack): ValidationError[] {
  const errors: ValidationError[] = [];
  const seenIds = new Set<string>();

  if (!pack.id || !pack.name) {
    errors.push({ packId: pack.id ?? "unknown", message: "Missing id or name" });
  }

  if (!pack.prompts || pack.prompts.length === 0) {
    errors.push({ packId: pack.id, message: "Pack has no prompts" });
    return errors;
  }

  for (const prompt of pack.prompts) {
    if (seenIds.has(prompt.id)) {
      errors.push({ packId: pack.id, promptId: prompt.id, message: "Duplicate prompt id" });
    }
    seenIds.add(prompt.id);

    if (!prompt.text || prompt.text.trim().length === 0) {
      errors.push({ packId: pack.id, promptId: prompt.id, message: "Empty prompt text" });
    }

    if (!pack.categories.includes(prompt.category)) {
      errors.push({
        packId: pack.id,
        promptId: prompt.id,
        message: `Category "${prompt.category}" not in pack categories [${pack.categories.join(", ")}]`,
      });
    }

    if (!["easy", "medium", "hard"].includes(prompt.difficulty)) {
      errors.push({
        packId: pack.id,
        promptId: prompt.id,
        message: `Invalid difficulty "${prompt.difficulty}"`,
      });
    }
  }

  return errors;
}

// Loader with filtering

interface LoadOptions {
  categories?: string[];
  difficulty?: Prompt["difficulty"];
  familySafeOnly?: boolean;
  locale?: string;
}

export function loadPack(filePath: string): PromptPack {
  const raw = readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as PromptPack;
}

export function filterPrompts(pack: PromptPack, opts: LoadOptions = {}): Prompt[] {
  return pack.prompts.filter((p) => {
    if (opts.categories && !opts.categories.includes(p.category)) return false;
    if (opts.difficulty && p.difficulty !== opts.difficulty) return false;
    if (opts.familySafeOnly && !p.familySafe) return false;
    if (opts.locale && p.locale !== opts.locale) return false;
    return true;
  });
}

// Shuffle using Fisher-Yates (unbiased)

export function shuffle<T>(arr: T[]): T[] {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

// Draw N unique prompts from a pack, respecting filters

export function drawPrompts(pack: PromptPack, count: number, opts: LoadOptions = {}): Prompt[] {
  const filtered = filterPrompts(pack, opts);
  const shuffled = shuffle(filtered);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

// CLI validation runner

function runCLIValidation(): void {
  const args = process.argv.slice(2);
  if (args[0] !== "--validate" || args.length < 2) {
    console.log("Usage: npx tsx prompt-pack.schema.ts --validate ./content/packs/*.json");
    process.exit(1);
  }

  const files = args.slice(1);
  let totalErrors = 0;

  for (const file of files) {
    try {
      const pack = loadPack(file);
      const errors = validatePack(pack);
      if (errors.length > 0) {
        console.error(`\n${file}: ${errors.length} error(s)`);
        for (const e of errors) console.error(`  - [${e.promptId ?? "pack"}] ${e.message}`);
        totalErrors += errors.length;
      } else {
        console.log(`${file}: OK (${pack.prompts.length} prompts)`);
      }
    } catch (err) {
      console.error(`${file}: Failed to parse - ${(err as Error).message}`);
      totalErrors++;
    }
  }

  process.exit(totalErrors > 0 ? 1 : 0);
}

if (process.argv[1]?.endsWith("prompt-pack.schema.ts")) {
  runCLIValidation();
}
