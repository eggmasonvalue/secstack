import {
  type BuildSystemPromptOptions,
  type ExtensionAPI,
} from "@earendil-works/pi-coding-agent";

const DEFAULT_TOOLS = ["read", "bash", "edit", "write"];

function formatToolEnvelope(options: BuildSystemPromptOptions): string {
  const tools = options.selectedTools ?? DEFAULT_TOOLS;
  const snippets = Object.entries(options.toolSnippets ?? {});
  const toolsList =
    snippets.length > 0
      ? snippets.map(([name, snippet]) => `- ${name}: ${snippet}`).join("\n")
      : "(none)";

  const guidelines: string[] = [];
  const seen = new Set<string>();
  const addGuideline = (guideline: string) => {
    if (!seen.has(guideline)) {
      seen.add(guideline);
      guidelines.push(guideline);
    }
  };

  if (
    tools.includes("bash") &&
    !tools.includes("grep") &&
    !tools.includes("find") &&
    !tools.includes("ls")
  ) {
    addGuideline("Use bash for file operations like ls, rg, find");
  }
  for (const guideline of options.promptGuidelines ?? []) {
    const normalized = guideline.trim();
    if (normalized) addGuideline(normalized);
  }
  addGuideline("Be concise in your responses");
  addGuideline("Show file paths clearly when working with files");

  return `Available tools:
${toolsList}

In addition to the tools above, you may have access to other custom tools depending on the project.

Guidelines:
${guidelines.map((guideline) => `- ${guideline}`).join("\n")}`;
}

export default function systemPromptExtension(pi: ExtensionAPI) {
  pi.on("before_agent_start", (event) => {
    const customPrompt = event.systemPromptOptions.customPrompt;
    if (!customPrompt || !event.systemPrompt.startsWith(customPrompt)) return;

    const remainder = event.systemPrompt.slice(customPrompt.length);
    return {
      systemPrompt: `${customPrompt}\n\n${formatToolEnvelope(event.systemPromptOptions)}${remainder}`,
    };
  });
}
