// Descobre workflows em <repo>/workflows/*.ts (ou .js após build) e os carrega por nome.

import { readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import type { WorkflowDefinition } from "./workflow.js";

export function workflowsDir(): string {
  return resolve(process.env.WORKFLOWS_DIR ?? join(import.meta.dirname, "..", "..", "workflows"));
}

export async function loadWorkflows(): Promise<Map<string, WorkflowDefinition<any, any>>> {
  const dir = workflowsDir();
  const found = new Map<string, WorkflowDefinition<any, any>>();
  for (const file of readdirSync(dir)) {
    if (!/\.(ts|js|mjs)$/.test(file) || file.endsWith(".d.ts")) continue;
    const mod = (await import(pathToFileURL(join(dir, file)).href)) as { default?: WorkflowDefinition<any, any> };
    if (mod.default?.meta?.name) found.set(mod.default.meta.name, mod.default);
  }
  return found;
}
