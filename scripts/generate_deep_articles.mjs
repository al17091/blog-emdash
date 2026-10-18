// Generator for deep A4-report class articles for blog-emdash
import fs from "fs";
import path from "path";

const seedPath = path.resolve("seed/seed.json");
const seed = JSON.parse(fs.readFileSync(seedPath, "utf-8"));

function makeBlock(text, style = "normal") {
  return {
    _type: "block",
    style,
    _key: "k_" + Math.random().toString(36).substring(2, 10),
    children: [
      {
        _type: "span",
        _key: "s_" + Math.random().toString(36).substring(2, 10),
        text
      }
    ]
  };
}

function parseMarkdownToBlocks(markdown) {
  const lines = markdown.split("\n");
  const blocks = [];
  let buffer = [];

  const flushBuffer = () => {
    if (buffer.length > 0) {
      const text = buffer.join(" ").trim();
      if (text) {
        blocks.push(makeBlock(text, "normal"));
      }
      buffer = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trimEnd();
    const trimmed = line.trim();

    if (!trimmed) {
      flushBuffer();
      continue;
    }

    if (trimmed.startsWith("### ")) {
      flushBuffer();
      blocks.push(makeBlock(trimmed.substring(4), "h3"));
    } else if (trimmed.startsWith("## ")) {
      flushBuffer();
      blocks.push(makeBlock(trimmed.substring(3), "h2"));
    } else if (trimmed.startsWith("> ")) {
      flushBuffer();
      blocks.push(makeBlock(trimmed.substring(2), "blockquote"));
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ") || /^\d+\.\s/.test(trimmed)) {
      flushBuffer();
      blocks.push(makeBlock(trimmed, "normal"));
    } else if (trimmed.startsWith("```")) {
      flushBuffer();
      // collect code lines until next ```
      let codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      blocks.push(makeBlock(codeLines.join("\n"), "normal"));
    } else {
      buffer.push(trimmed);
    }
  }
  flushBuffer();
  return blocks;
}

export { seed, makeBlock, parseMarkdownToBlocks, seedPath };

