import { createMarkdownProcessor, type MarkdownProcessor } from "@astrojs/markdown-remark";

let processorPromise: Promise<MarkdownProcessor> | null = null;

function getProcessor(): Promise<MarkdownProcessor> {
	if (!processorPromise) {
		processorPromise = createMarkdownProcessor({
			gfm: true,
			syntaxHighlight: {
				type: "shiki",
				excludeLangs: ["math"],
			},
		});
	}
	return processorPromise;
}

/**
 * Render raw Markdown string to semantic HTML using Astro's native Remark/Rehype/GFM/Shiki pipeline.
 */
export async function renderMarkdown(markdown: string): Promise<string> {
	if (!markdown || !markdown.trim()) return "";
	const processor = await getProcessor();
	const { code } = await processor.render(markdown);
	return code;
}

