/**
 * build-book.mjs
 * Book & Long-Form Publishing Pipeline
 * Composes a book from Markdown articles and renders EPUB3 + PDF via Pandoc.
 *
 * Usage: node books/scripts/build-book.mjs <slug> [--compose-only|--render-only]
 * Or:    npm run build:book -- <slug>
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';
import yaml from 'js-yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '../../');
const ALLOWED_TOP_LEVEL_FIELDS = new Set([
  'title',
  'subtitle',
  'author',
  'version',
  'description',
  'language',
  'cover_image',
  'publisher',
  'rights',
  'identifier',
  'date',
  'subjects',
  'output',
  'frontmatter',
  'parts',
  'chapters',
  'appendices',
]);

const ALLOWED_ITEM_FIELDS = new Set([
  'source',
  'title',
  'role',
  'part',
  'numbered',
  'number',
]);

// ---------------------------------------------------------------------------
// Progress logger (FR-012)
// ---------------------------------------------------------------------------
function log(message) {
  console.log(`[book-publishing] ${message}`);
}

function warn(message) {
  console.warn(`[book-publishing] WARNING: ${message}`);
}

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// T005 — Slug validation
// ---------------------------------------------------------------------------
const SLUG_REGEX = /^[a-z0-9-]+$/;

function validateSlug(slug) {
  if (!slug) {
    fail('No slug provided. Usage: npm run build:book -- <slug>');
  }
  if (!SLUG_REGEX.test(slug)) {
    fail(`slug must be lowercase alphanumeric with hyphens only. Got: "${slug}"`);
  }
}

function validateBookItem(item, fieldName, index) {
  if (!item || typeof item !== 'object' || Array.isArray(item)) {
    fail(`book.yaml ${fieldName}[${index}] must be an object.`);
  }
  for (const key of Object.keys(item)) {
    if (!ALLOWED_ITEM_FIELDS.has(key)) {
      fail(`book.yaml ${fieldName}[${index}] has unsupported field "${key}".`);
    }
  }
  if (!item.source) {
    fail(`book.yaml ${fieldName}[${index}] is missing required field "source".`);
  }
}

function validateBookItems(items, fieldName) {
  if (items == null) return;
  if (!Array.isArray(items)) {
    fail(`book.yaml field "${fieldName}" must be an array.`);
  }
  items.forEach((item, index) => validateBookItem(item, fieldName, index));
}

function validateParts(parts) {
  if (parts == null) return;
  if (!Array.isArray(parts)) {
    fail('book.yaml field "parts" must be an array.');
  }
  parts.forEach((part, index) => {
    if (!part || typeof part !== 'object' || Array.isArray(part)) {
      fail(`book.yaml parts[${index}] must be an object.`);
    }
    const allowedPartFields = new Set(['title', 'chapters']);
    for (const key of Object.keys(part)) {
      if (!allowedPartFields.has(key)) {
        fail(`book.yaml parts[${index}] has unsupported field "${key}".`);
      }
    }
    if (!part.title) {
      fail(`book.yaml parts[${index}] is missing required field "title".`);
    }
    validateBookItems(part.chapters || [], `parts[${index}].chapters`);
  });
}

function getManifestChapters(book) {
  const chapters = [];

  if (Array.isArray(book.chapters)) {
    chapters.push(...book.chapters);
  }

  if (Array.isArray(book.parts)) {
    for (const part of book.parts) {
      if (Array.isArray(part.chapters)) {
        chapters.push(...part.chapters);
      }
    }
  }

  return chapters;
}

// ---------------------------------------------------------------------------
// T006 — parseBookYaml
// ---------------------------------------------------------------------------
function parseBookYaml(slug) {
  const bookYamlPath = path.join(REPO_ROOT, 'books', slug, 'book.yaml');

  if (!fs.existsSync(bookYamlPath)) {
    fail(`book.yaml not found at books/${slug}/book.yaml`);
  }

  let book;
  try {
    const raw = fs.readFileSync(bookYamlPath, 'utf8');
    book = yaml.load(raw);
  } catch (err) {
    fail(`Failed to parse books/${slug}/book.yaml — ${err.message}`);
  }

  if (!book || typeof book !== 'object' || Array.isArray(book)) {
    fail('book.yaml must contain a YAML object.');
  }

  for (const key of Object.keys(book)) {
    if (!ALLOWED_TOP_LEVEL_FIELDS.has(key)) {
      fail(`book.yaml has unsupported top-level field "${key}". Supported fields: ${Array.from(ALLOWED_TOP_LEVEL_FIELDS).sort().join(', ')}`);
    }
  }

  // Validate required fields
  const missing = [];
  if (!book.title) missing.push('title');
  if (!book.author) missing.push('author');
  if (!book.output?.formats?.length) missing.push('output.formats');
  if (!book.chapters && !book.parts) missing.push('chapters or parts');

  if (missing.length > 0) {
    fail(`book.yaml is missing required fields: ${missing.join(', ')}`);
  }

  if (!Array.isArray(book.output.formats)) {
    fail('book.yaml field "output.formats" must be an array.');
  }

  // Validate supported formats
  const supportedFormats = ['epub', 'pdf'];
  for (const fmt of book.output.formats) {
    if (!supportedFormats.includes(fmt)) {
      fail(`Unsupported output format "${fmt}". Supported: ${supportedFormats.join(', ')}`);
    }
  }

  validateBookItems(book.frontmatter || [], 'frontmatter');
  validateBookItems(book.chapters || [], 'chapters');
  validateBookItems(book.appendices || [], 'appendices');
  validateParts(book.parts);

  // FR-013: minimum 2 chapters
  const manifestChapters = getManifestChapters(book);
  if (manifestChapters.length < 2) {
    fail(`Minimum 2 chapters required. Found: ${manifestChapters.length}.`);
  }

  return book;
}

// ---------------------------------------------------------------------------
// T007 — stripFrontmatter
// Returns { body: string, frontmatter: object }
// ---------------------------------------------------------------------------
function stripFrontmatter(markdownContent) {
  const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n/;
  const match = markdownContent.match(frontmatterRegex);

  if (!match) {
    return { body: markdownContent, frontmatter: {} };
  }

  const frontmatterText = match[1];
  let frontmatter = {};
  try {
    frontmatter = yaml.load(frontmatterText) || {};
  } catch (err) {
    warn(`Could not parse frontmatter YAML — ${err.message}`);
  }

  const body = markdownContent.slice(match[0].length).trimStart();
  if (!body) {
    warn('Article body is empty after stripping frontmatter.');
  }

  return { body, frontmatter };
}

// ---------------------------------------------------------------------------
// T008 — resolveChapterTitle
// ---------------------------------------------------------------------------
function resolveChapterTitle(chapter, frontmatter, sourceFile) {
  if (chapter.title) return chapter.title;
  if (frontmatter.title) return frontmatter.title;
  if (frontmatter.name) return frontmatter.name;
  return path.basename(sourceFile, '.md');
}

function stripNumberingPrefix(title) {
  return String(title)
    .replace(/^chapter\s+[0-9]+[a-z]?[:.]\s*/i, '')
    .replace(/^appendix\s+[a-z0-9]+[:.]\s*/i, '')
    .trim();
}

function buildHeading(entry, displayTitle, counters) {
  const role = entry.role || 'chapter';
  const numbered = entry.numbered !== false;

  if (role === 'frontmatter' || role === 'foreword' || role === 'introduction') {
    return `# ${displayTitle}`;
  }

  if (role === 'appendix') {
    const letter = String.fromCharCode(64 + counters.appendix);
    return displayTitle.toLowerCase().startsWith(`appendix ${letter.toLowerCase()}:`)
      ? `# ${displayTitle}`
      : `# Appendix ${letter}: ${stripNumberingPrefix(displayTitle)}`;
  }

  if (!numbered) {
    return `# ${displayTitle}`;
  }

  const chapterLabel = entry.number || counters.chapter;
  return `# Chapter ${chapterLabel}: ${stripNumberingPrefix(displayTitle)}`;
}

// ---------------------------------------------------------------------------
// processBodyForBook — clean up article body for book inclusion
//   1. Strip leading heading if it duplicates the chapter title (web articles
//      carry their own H2 title that conflicts with the injected # Chapter N)
//   2. Convert relative images to italicised alt-text captions
//   3. Convert site-internal links (/blog/...) to plain text
// ---------------------------------------------------------------------------
function processBodyForBook(body, chapterTitle) {
  let text = body;

  // 1. Strip leading H1-H3 if it overlaps significantly with the chapter title
  const firstLineMatch = text.match(/^(#{1,3})\s+(.+)/);
  if (firstLineMatch) {
    const normalize = (s) =>
      s.toLowerCase().replace(/[^a-z0-9\s]/g, '').trim();
    const headingWords = normalize(firstLineMatch[2]).split(/\s+/).filter((w) => w.length >= 3);
    const titleWords = new Set(normalize(chapterTitle).split(/\s+/).filter((w) => w.length >= 3));
    const overlap =
      headingWords.filter((w) => titleWords.has(w)).length /
      Math.max(headingWords.length, 1);
    if (overlap >= 0.5) {
      // Remove the heading line and any blank lines immediately after it
      text = text.replace(/^#{1,3}\s+.+\r?\n(\s*\r?\n)*/, '');
    }
  }

  // 2. Relative images — replace with italicised alt text so the caption survives
  //    ![alt text](/img/...) → *[Image: alt text]*
  text = text.replace(/!\[([^\]]*)\]\(\/[^)]+\)/g, (_, alt) =>
    alt ? `*[Image: ${alt}]*` : ''
  );

  // 3. Internal site links — strip the URL, keep the link text
  //    [Link text](/blog/some-post/) → Link text
  text = text.replace(/\[([^\]]+)\]\(\/[^)]*\)/g, '$1');

  return text.trimStart();
}

// ---------------------------------------------------------------------------
// T009 — composeBook
// ---------------------------------------------------------------------------
function composeEntry(bookEntry, slug, seenOrders, counters, totalEntries) {
  const srcPath = path.join(REPO_ROOT, bookEntry.source);

  if (!fs.existsSync(srcPath)) {
    fail(`Chapter source not found: ${bookEntry.source}`);
  }

  const raw = fs.readFileSync(srcPath, 'utf8');
  const { body, frontmatter } = stripFrontmatter(raw);

  if (frontmatter.book_order != null) {
    if (seenOrders.has(frontmatter.book_order)) {
      warn(`Duplicate book_order value detected: ${frontmatter.book_order}. Using YAML declaration order as tiebreaker.`);
    } else {
      seenOrders.add(frontmatter.book_order);
    }
  }

  if (!body || !body.trim()) {
    warn(`Chapter source "${bookEntry.source}" has no body content — skipping.`);
    return [];
  }

  if (bookEntry.role === 'appendix') {
    counters.appendix++;
  } else if (!['frontmatter', 'foreword', 'introduction'].includes(bookEntry.role || 'chapter') && !bookEntry.number) {
    counters.chapter++;
  }

  const rawTitle = resolveChapterTitle(bookEntry, frontmatter, bookEntry.source);
  const heading = buildHeading(bookEntry, rawTitle, counters);
  const displayTitle = heading.replace(/^#\s+/, '');
  log(`Composing ${counters.entry}/${totalEntries}: "${displayTitle}"`);

  const cleanBody = processBodyForBook(body.trim(), rawTitle);

  return [
    heading,
    '',
    cleanBody,
    '',
    '---',
    '',
  ];
}

function composeBook(book, slug) {
  const manuscriptParts = [];
  const totalEntries =
    (book.frontmatter?.length || 0) +
    getManifestChapters(book).length +
    (book.appendices?.length || 0);
  const parts = [];

  // Compose chapters (duplicate book_order detection runs inline — one read per file).
  // Title, subtitle, and author are supplied as Pandoc metadata so PDF/EPUB
  // generators own title-page rendering instead of duplicating it in the body.
  const seenOrders = new Set();
  const counters = { chapter: 0, appendix: 0, entry: 0 };

  for (const item of book.frontmatter || []) {
    manuscriptParts.push({ ...item, role: item.role || 'frontmatter' });
  }

  if (Array.isArray(book.parts) && book.parts.length > 0) {
    for (const part of book.parts) {
      manuscriptParts.push({ type: 'part', title: part.title });
      for (const chapter of part.chapters || []) {
        manuscriptParts.push({ ...chapter, role: chapter.role || 'chapter' });
      }
    }
  } else {
    for (const chapter of book.chapters || []) {
      manuscriptParts.push({ ...chapter, role: chapter.role || 'chapter' });
    }
  }

  for (const appendix of book.appendices || []) {
    manuscriptParts.push({ ...appendix, role: 'appendix' });
  }

  for (const entry of manuscriptParts) {
    if (entry.type === 'part') {
      parts.push(`# ${entry.title}`);
      parts.push('');
      parts.push('---');
      parts.push('');
      continue;
    }

    counters.entry++;
    parts.push(...composeEntry(entry, slug, seenOrders, counters, totalEntries));
  }

  return parts.join('\n');
}

// ---------------------------------------------------------------------------
// T010 — writeCompiledBook
// ---------------------------------------------------------------------------
function writeCompiledBook(slug, content) {
  const bookDir = path.join(REPO_ROOT, 'books', slug);
  fs.mkdirSync(bookDir, { recursive: true });

  const outPath = path.join(bookDir, 'book.md');
  fs.writeFileSync(outPath, content, 'utf8');
  log(`Writing books/${slug}/book.md`);
}

// ---------------------------------------------------------------------------
// T011 — renderBook
// ---------------------------------------------------------------------------
function renderBook(slug, book, pdfEngine = 'xelatex') {
  const inputPath = path.join(REPO_ROOT, 'books', slug, 'book.md');
  const outputDir = path.join(REPO_ROOT, 'books', 'publish', slug);
  fs.mkdirSync(outputDir, { recursive: true });

  const language = book.language || 'en';
  const failures = [];

  for (const fmt of book.output.formats) {
    const ext = fmt === 'epub' ? 'epub' : 'pdf';
    const outputFile = path.join(outputDir, `book.${ext}`);

    // Common metadata flags
    const metaArgs = [
      '--metadata', `title:${book.title}`,
      '--metadata', `author:${book.author}`,
      '--metadata', `lang:${language}`,
    ];
    if (book.version) {
      metaArgs.push('--metadata', `version:${book.version}`);
    }
    if (book.subtitle) {
      metaArgs.push('--metadata', `subtitle:${book.subtitle}`);
    }
    if (book.description) {
      metaArgs.push('--metadata', `description:${book.description}`);
    }
    if (book.publisher) {
      metaArgs.push('--metadata', `publisher:${book.publisher}`);
    }
    if (book.rights) {
      metaArgs.push('--metadata', `rights:${book.rights}`);
    }
    if (book.identifier) {
      metaArgs.push('--metadata', `identifier:${book.identifier}`);
    }
    if (book.date) {
      metaArgs.push('--metadata', `date:${book.date}`);
    }
    for (const subject of book.subjects || []) {
      metaArgs.push('--metadata', `subject:${subject}`);
    }

    let pandocArgs;
    if (fmt === 'epub') {
      pandocArgs = [
        inputPath,
        '-o', outputFile,
        '--to', 'epub3',
        '--toc',
        '--toc-depth=2',
        ...metaArgs,
      ];
      if (book.cover_image) {
        const coverPath = path.resolve(REPO_ROOT, book.cover_image);
        if (!coverPath.startsWith(REPO_ROOT + path.sep) && coverPath !== REPO_ROOT) {
          console.error(`Error: cover_image path must be within the repository: "${book.cover_image}"`);
          process.exit(1);
        }
        pandocArgs.push('--epub-cover-image', coverPath);
      }
    } else if (fmt === 'pdf') {
      pandocArgs = [
        inputPath,
        '-o', outputFile,
        '--to', 'pdf',
        `--pdf-engine=${pdfEngine}`,
        '--toc',
        '--toc-depth=1',
        ...metaArgs,
      ];
      // LaTeX-specific variables — only applies when pdflatex/xelatex/lualatex is the engine
      if (pdfEngine === 'pdflatex' || pdfEngine === 'xelatex' || pdfEngine === 'lualatex') {
        pandocArgs.push(
          '--variable', 'documentclass=book',
          '--variable', 'classoption=oneside,openany',
          '--variable', 'geometry:paperwidth=7in',
          '--variable', 'geometry:paperheight=9.25in',
          '--variable', 'geometry:inner=0.8in',
          '--variable', 'geometry:outer=0.65in',
          '--variable', 'geometry:top=0.75in',
          '--variable', 'geometry:bottom=0.85in',
          '--variable', 'fontsize=10.5pt',
          '--variable', 'indent=true',
          '--include-in-header', path.join(REPO_ROOT, 'books', 'styles', 'book-pdf-header.tex')
        );
      }
    }

    log(`Rendering ${fmt.toUpperCase()}...`);
    const result = spawnSync('pandoc', pandocArgs, {
      maxBuffer: 20 * 1024 * 1024,
      encoding: 'utf8',
    });

    if (result.status !== 0) {
      if (result.error?.code === 'ENOBUFS') {
        failures.push({
          format: fmt,
          message: `Error: Pandoc output exceeded buffer limit for format "${fmt}". This is a build script configuration issue, not a Pandoc rendering error.`,
        });
      } else if (result.error?.code === 'ENOENT') {
        failures.push({
          format: fmt,
          message: `Error: pandoc binary not found when attempting to render "${fmt}".`,
        });
      } else {
        const stderr = result.stderr || result.error?.message || 'unknown error';
        failures.push({
          format: fmt,
          message: `Error: Pandoc rendering failed for format "${fmt}": ${stderr.trim()}`,
        });
      }
    }
  }

  return failures;
}

// ---------------------------------------------------------------------------
// T012 — availability checks
// Returns resolved PDF engine name for use by renderBook.
// On Windows, also probes the default Pandoc install location and adds it to PATH
// if pandoc is not already resolvable from the current PATH.
// ---------------------------------------------------------------------------
function checkAvailability(book) {
  // (a) Pandoc — probe PATH first, then Windows default location
  let pandocResult = spawnSync('pandoc', ['--version'], { maxBuffer: 1024 * 1024, encoding: 'utf8' });

  if (pandocResult.status !== 0 || pandocResult.error) {
    // Windows: Pandoc installs to %LOCALAPPDATA%\Pandoc\ by default
    if (process.platform === 'win32' && process.env.LOCALAPPDATA) {
      const winPandocDir = path.join(process.env.LOCALAPPDATA, 'Pandoc');
      process.env.PATH = `${winPandocDir}${path.delimiter}${process.env.PATH}`;
      pandocResult = spawnSync('pandoc', ['--version'], { maxBuffer: 1024 * 1024, encoding: 'utf8' });
    }
    if (pandocResult.status !== 0 || pandocResult.error) {
      console.error('Error: Pandoc not found. Install from https://pandoc.org/installing.html');
      process.exit(1);
    }
  }

  // Parse version and warn if below 2.19
  const versionLine = (pandocResult.stdout || '').split('\n')[0];
  const versionMatch = versionLine.match(/pandoc\s+(\d+)\.(\d+)/i);
  if (versionMatch) {
    const major = parseInt(versionMatch[1], 10);
    const minor = parseInt(versionMatch[2], 10);
    if (major < 2 || (major === 2 && minor < 19)) {
      warn(`Pandoc version ${major}.${minor} detected. Minimum recommended is 2.19. EPUB3 metadata handling may differ.`);
    }
  }

  // (b) PDF engine — prefer Unicode-capable engines before pdflatex.
  let pdfEngine = null;
  if (book.output.formats.includes('pdf')) {
    const engines = ['xelatex', 'lualatex', 'pdflatex', 'typst'];
    for (const engine of engines) {
      const r = spawnSync(engine, ['--version'], { maxBuffer: 1024 * 1024, encoding: 'utf8' });
      if (r.status === 0 && !r.error) {
        pdfEngine = engine;
        if (engine === 'pdflatex') {
          warn('Using pdflatex for PDF output. Unicode characters may require xelatex or lualatex.');
        } else if (engine === 'typst') {
          warn('No LaTeX PDF engine found — using typst. Output formatting may differ from LaTeX.');
        }
        break;
      }
    }
    if (!pdfEngine) {
      console.error(
        'Error: No PDF engine found. Install one of:\n' +
        '  xelatex/lualatex/pdflatex — TeX Live (Linux/macOS) or MiKTeX (Windows) — https://miktex.org/download\n' +
        '  typst                    — https://github.com/typst/typst/releases\n' +
        'See quickstart.md for installation instructions.'
      );
      process.exit(1);
    }
  }

  return pdfEngine;
}

function validateArtifacts(slug) {
  log('Validating artifacts...');
  const result = spawnSync(
    process.execPath,
    [path.join(REPO_ROOT, 'books', 'scripts', 'validate-book.mjs'), slug],
    {
      cwd: REPO_ROOT,
      encoding: 'utf8',
      maxBuffer: 20 * 1024 * 1024,
    }
  );

  if (result.stdout) {
    process.stdout.write(result.stdout);
  }
  if (result.stderr) {
    process.stderr.write(result.stderr);
  }
  if (result.status !== 0 || result.error) {
    const message = result.error?.message || `validation exited ${result.status}`;
    fail(`Book artifact validation failed: ${message}`);
  }
}

// ---------------------------------------------------------------------------
// T013 — Main execution flow
// ---------------------------------------------------------------------------
function main() {
  const slug = process.argv[2];
  const args = new Set(process.argv.slice(3));
  const lifecycle = process.env.npm_lifecycle_event || '';
  const composeOnly = args.has('--compose-only') || lifecycle === 'book:compose';
  const renderOnly = args.has('--render-only') || lifecycle === 'book:render';
  const skipValidation = args.has('--no-validate');

  if (composeOnly && renderOnly) {
    fail('Use only one of --compose-only or --render-only.');
  }

  // T005: Validate slug
  validateSlug(slug);

  // T006: Parse and validate book.yaml
  const book = parseBookYaml(slug);

  log(`Parsing book.yaml: "${book.title}"`);

  let pdfEngine = null;
  if (!composeOnly) {
    // T012: Availability checks — returns resolved PDF engine (null if no pdf format)
    pdfEngine = checkAvailability(book);
  }

  if (!renderOnly) {
    // T009: Compose book
    log('Starting composition...');
    const composedContent = composeBook(book, slug);

    // T010: Write compiled book.md
    writeCompiledBook(slug, composedContent);
  }

  if (composeOnly) {
    log(`Done. Output: books/${slug}/book.md`);
    return;
  }

  // T011: Render all formats
  const failures = renderBook(slug, book, pdfEngine);

  if (failures.length > 0) {
    process.stderr.write(
      `Warning: books/${slug}/book.md was written but not all formats rendered successfully. Resolve rendering failures before committing books/${slug}/book.md.\n`
    );
    for (const failure of failures) {
      process.stderr.write(`${failure.message}\n`);
    }
    process.exit(1);
  }

  const outputDir = `books/publish/${slug}`;
  const outputFiles = book.output.formats
    .map((fmt) => `${outputDir}/book.${fmt === 'epub' ? 'epub' : 'pdf'}`)
    .join(', ');

  if (!skipValidation) {
    validateArtifacts(slug);
  }

  log(`Done. Output: ${outputFiles}`);
}

main();
