/**
 * validate-book.mjs
 * Artifact validation for generated EPUB/PDF books.
 *
 * Usage: node books/scripts/validate-book.mjs <slug>
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';
import yaml from 'js-yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '../../');
const SLUG_REGEX = /^[a-z0-9-]+$/;
const MIN_EPUB_BYTES = 1024;
const MIN_PDF_BYTES = 10 * 1024;

function log(message) {
  console.log(`[book-validation] ${message}`);
}

function warn(message) {
  console.warn(`[book-validation] WARNING: ${message}`);
}

function fail(message) {
  console.error(`[book-validation] ERROR: ${message}`);
  process.exitCode = 1;
}

function run(command, args) {
  return spawnSync(command, args, {
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
  });
}

function readBook(slug) {
  if (!slug || !SLUG_REGEX.test(slug)) {
    console.error('Error: slug must be lowercase alphanumeric with hyphens only.');
    process.exit(1);
  }

  const yamlPath = path.join(REPO_ROOT, 'books', slug, 'book.yaml');
  if (!fs.existsSync(yamlPath)) {
    console.error(`Error: book.yaml not found at books/${slug}/book.yaml`);
    process.exit(1);
  }

  return yaml.load(fs.readFileSync(yamlPath, 'utf8'));
}

function checkFile(filePath, label, minBytes) {
  if (!fs.existsSync(filePath)) {
    fail(`${label} missing: ${path.relative(REPO_ROOT, filePath)}`);
    return false;
  }

  const size = fs.statSync(filePath).size;
  if (size < minBytes) {
    fail(`${label} too small (${size} bytes): ${path.relative(REPO_ROOT, filePath)}`);
    return false;
  }

  log(`${label} exists (${Math.round(size / 1024)} KB)`);
  return true;
}

function checkNoDuplicateNumbering(text, label) {
  const patterns = [
    /Chapter\s+\d+\s*:\s*Chapter\s+\d+/i,
    /Chapter\s+\d+\s*:\s*Appendix\s+[A-Z0-9]+/i,
    /Appendix\s+[A-Z0-9]+\s*:\s*Appendix\s+[A-Z0-9]+/i,
  ];
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      fail(`${label} contains duplicate numbering: "${match[0]}"`);
    }
  }
}

function validateBookMarkdown(slug) {
  const mdPath = path.join(REPO_ROOT, 'books', slug, 'book.md');
  if (!checkFile(mdPath, 'Compiled Markdown', MIN_EPUB_BYTES)) return;
  const text = fs.readFileSync(mdPath, 'utf8');
  checkNoDuplicateNumbering(text, 'book.md');
}

function validateEpub(epubPath) {
  if (!checkFile(epubPath, 'EPUB', MIN_EPUB_BYTES)) return;

  const listing = run('tar', ['-tf', epubPath]);
  if (listing.status !== 0) {
    fail(`EPUB is not readable as a zip archive: ${listing.stderr || listing.error?.message || 'unknown error'}`);
    return;
  }

  const files = new Set(listing.stdout.split(/\r?\n/).filter(Boolean));
  for (const required of ['mimetype', 'META-INF/container.xml', 'EPUB/content.opf', 'EPUB/nav.xhtml']) {
    if (!files.has(required)) {
      fail(`EPUB missing required file: ${required}`);
    }
  }

  const nav = run('tar', ['-xOf', epubPath, 'EPUB/nav.xhtml']);
  if (nav.status === 0) {
    checkNoDuplicateNumbering(nav.stdout, 'EPUB TOC');
  } else {
    fail(`Could not inspect EPUB TOC: ${nav.stderr || nav.error?.message || 'unknown error'}`);
  }

  const epubcheck = run('epubcheck', [epubPath]);
  if (epubcheck.error?.code === 'ENOENT') {
    warn('epubcheck not found; install epubcheck for full EPUB structural validation.');
  } else if (epubcheck.status !== 0) {
    fail(`epubcheck failed:\n${(epubcheck.stdout || '')}${(epubcheck.stderr || '')}`.trim());
  } else {
    log('epubcheck passed');
  }
}

function validatePdf(pdfPath) {
  if (!checkFile(pdfPath, 'PDF', MIN_PDF_BYTES)) return;

  const buffer = fs.readFileSync(pdfPath);
  if (!buffer.subarray(0, 5).toString('ascii').startsWith('%PDF')) {
    fail('PDF does not start with a %PDF header.');
  }

  const pdfinfo = run('pdfinfo', [pdfPath]);
  if (pdfinfo.status === 0) {
    const match = pdfinfo.stdout.match(/^Pages:\s+(\d+)/m);
    const pages = match ? Number(match[1]) : 0;
    if (pages <= 0) {
      fail('PDF page count could not be determined by pdfinfo.');
    } else {
      log(`PDF page count: ${pages}`);
    }
  } else {
    const text = buffer.toString('latin1');
    const pages = (text.match(/\/Type\s*\/Page\b/g) || []).length;
    if (pages <= 0) {
      fail('PDF page count fallback found no pages.');
    } else {
      log(`PDF page count fallback: ${pages}`);
    }
  }

  checkNoDuplicateNumbering(buffer.toString('latin1'), 'PDF');
}

function main() {
  const slug = process.argv[2];
  const book = readBook(slug);
  const outputDir = path.join(REPO_ROOT, 'books', 'publish', slug);

  validateBookMarkdown(slug);

  for (const format of book.output?.formats || []) {
    if (format === 'epub') {
      validateEpub(path.join(outputDir, 'book.epub'));
    } else if (format === 'pdf') {
      validatePdf(path.join(outputDir, 'book.pdf'));
    }
  }

  if (process.exitCode) {
    process.exit(process.exitCode);
  }

  log(`Validation passed for ${slug}`);
}

main();
