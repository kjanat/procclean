#!/usr/bin/env bun
/**
 * Format JavaScript embedded in GitHub Actions workflow YAML files.
 * Uses yq + dprint to extract, format, and re-insert script blocks.
 */

import { parseArgs } from "util";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    help: { type: "boolean", short: "h" },
    check: { type: "boolean", short: "c" },
    verbose: { type: "boolean", short: "v" },
  },
  allowPositionals: true,
});

if (values.help) {
  console.log(`Usage: bun scripts/format-workflow-scripts.ts [options] [file...]

Options:
  -h, --help     Show this help message
  -c, --check    Check if files need formatting (exit 1 if changes needed)
  -v, --verbose  Show detailed output

Examples:
  bun scripts/format-workflow-scripts.ts
  bun scripts/format-workflow-scripts.ts .github/workflows/ci.yml
  bun scripts/format-workflow-scripts.ts --check
`);
  process.exit(0);
}

/**
 * Format JavaScript source and return the formatted result.
 *
 * @param code - JavaScript source to format
 * @returns The formatted code with a trailing newline removed if present, or `null` when formatting fails
 */
async function formatJs(code: string): Promise<string | null> {
  const proc = Bun.spawn(["dprint", "fmt", "--stdin=js"], {
    stdin: new TextEncoder().encode(code),
    stdout: "pipe",
    stderr: "pipe",
  });
  const stdout = await new Response(proc.stdout).text();
  const exitCode = await proc.exited;
  return exitCode === 0 ? stdout.replace(/\n$/, "") : null;
}

/**
 * Formats JavaScript code blocks under `script: |` in a GitHub Actions workflow YAML file.
 *
 * Detects indented `script: |` blocks, dedents their contents, runs the formatter, and reinserts
 * the formatted code with the original block indentation. Unparseable script blocks are left
 * unchanged. If changes are made and check mode is disabled, the file is overwritten; in check
 * mode the function only reports that the file would be changed.
 *
 * @param filePath - Path to the YAML workflow file to process
 * @returns `true` if the file was modified, `false` otherwise.
 */
async function processFile(filePath: string): Promise<boolean> {
  const content = await Bun.file(filePath).text();
  const lines = content.split("\n");

  // Find all "script: |" lines (reverse order to preserve line numbers)
  const scriptStarts: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    if (/^\s+script:\s*\|/.test(lines[i])) {
      scriptStarts.push(i);
    }
  }
  scriptStarts.reverse();

  if (scriptStarts.length === 0) return false;

  let modified = false;
  let newLines = [...lines];

  for (const startLine of scriptStarts) {
    const scriptLineMatch = lines[startLine].match(/^(\s+)script:\s*\|/);
    if (!scriptLineMatch) continue;

    const baseIndent = scriptLineMatch[1];
    const contentIndent = baseIndent + "  ";
    const contentStart = startLine + 1;

    // Find end of script block
    let contentEnd = lines.length - 1;
    for (let i = contentStart; i < lines.length; i++) {
      const line = lines[i];
      // Empty lines are part of the block
      if (line.trim() === "") continue;
      // If line has same or less indent and is not empty, we're done
      if (!line.startsWith(contentIndent) || (line.startsWith(baseIndent) && !line.startsWith(contentIndent))) {
        contentEnd = i - 1;
        break;
      }
    }

    // Extract and dedent script content
    const scriptLines = lines.slice(contentStart, contentEnd + 1);
    const script = scriptLines.map(l => l.slice(contentIndent.length)).join("\n").replace(/\n+$/, "");

    const formatted = await formatJs(script);
    if (!formatted) {
      if (values.verbose) console.log(`  Skipping unparseable script at line ${startLine + 1}`);
      continue;
    }

    if (formatted === script) continue;

    // Re-indent and replace (don't indent empty lines)
    const formattedLines = formatted.split("\n").map(l => l === "" ? "" : contentIndent + l);
    newLines = [
      ...newLines.slice(0, contentStart),
      ...formattedLines,
      ...newLines.slice(contentEnd + 1),
    ];
    modified = true;

    if (values.verbose) console.log(`  Formatted script at line ${startLine + 1}`);
  }

  if (modified && !values.check) {
    await Bun.write(filePath, newLines.join("\n") + "\n");
    console.log(`Formatted: ${filePath}`);
  } else if (modified && values.check) {
    console.log(`Would format: ${filePath}`);
  }

  return modified;
}

/**
 * Discover workflow YAML files and process each to format embedded JavaScript script blocks.
 *
 * If positional file paths were provided, those are used; otherwise all `*.yml` files under
 * `.github/workflows` are targeted. Prints "No workflow files found" and exits with code 0 when
 * no targets are found. Processes files sequentially, reporting per-file errors to stderr without
 * aborting the run. If run in check mode and any file would be modified, prints a summary message
 * and exits with code 1.
 */
async function main() {
  let files: string[];

  if (positionals.length > 0) {
    files = positionals;
  } else {
    const glob = new Bun.Glob("**/*.yml");
    files = Array.from(glob.scanSync({ cwd: ".github/workflows" })).map(f => `.github/workflows/${f}`);
  }

  if (files.length === 0) {
    console.log("No workflow files found");
    process.exit(0);
  }

  let anyModified = false;

  for (const file of files) {
    try {
      if (await processFile(file)) anyModified = true;
    } catch (e) {
      console.error(`Error processing ${file}: ${e}`);
    }
  }

  if (values.check && anyModified) {
    console.log("\nSome files need formatting.");
    process.exit(1);
  }
}

await main();
