// Music Metadata • copyright blasieuwu, 2026
// a better way of getting track metadata.
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { fileURLToPath } from 'url';

export const REQUIRED: ReadonlySet<string> = new Set([
  'title',
  'artist',
  'album',
  'explicit'
]);

export interface MDataResult {
  title?: string;
  artist?: string[];
  album?: string;
  explicit?: boolean;
  'romanized-title'?: string;
  'romanized-artist'?: string[];
  'search-links'?: string[];
  'playback-links'?: string[];
  lyrics?: string;
  [key: string]: any;
}

export interface TrackIdentity {
  title?: string;
  artist?: string[];
  explicit?: string;
}

export function validateMdata(
  fileName: string,
  silent: boolean = false,
  yields: boolean = false,
  trackIdentity?: (title: string, artist: string[]) => void
): MDataResult | null {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const filePath = path.resolve(currentDir, fileName);
  const fileExt = path.extname(fileName);

  if (!fs.existsSync(filePath)) {
    if (!silent) {
      console.log('\x1b[1;31m[1/2] [-] file wasn\'t located.\x1b[0m');
    }
    return null;
  }

  if (fileExt !== '.mdata') {
    if (!silent) {
      console.log(`\x1b[1;33m[2/2] [!] '${fileName}' is not a .mdata file...\x1b[0m`);
    }
    return null;
  }

  if (!silent) {
    console.log(`\n\x1b[1;32m--- processing ${fileName} ---\x1b[0m\n`);
  }

  const data: MDataResult = {};
  const errors: string[] = [];
  const warnings: string[] = [];
  let identified = false;

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split(/\r?\n/);

  lines.forEach((rawLine: string, index: number) => {
    const lineNum = index + 1;
    const line = rawLine.trim();

    // discard empty lines
    if (!line) return;

    // syntax check // square brackets
    if (!(line.startsWith('[') && line.endsWith(']')) || !line.includes(':')) {
      errors.push(`[${fileName}:${lineNum}] invalid syntax -> '${line}'`);
      return;
    }

    const innerContent = line.slice(1, -1).trim();
    const colonIdx = innerContent.indexOf(':');
    const key = innerContent.slice(0, colonIdx).trim().toLowerCase();
    const value = innerContent.slice(colonIdx + 1).trim();

    // syntax check // key/value args
    if (!key || !value) {
      errors.push(`[${fileName}:${lineNum}] empty key/value in '${line}'`);
      return;
    }

    // metadata checks
    if (key === 'explicit') {
      if (!['true', 'false'].includes(value.toLowerCase())) {
        errors.push(`[${fileName}:${lineNum}] 'explicit' must be 'true' or 'false'.`);
      } else {
        data[key] = value.toLowerCase() === 'true';
      }
    } else if (key === 'search-links' || key === 'playback-links') {
      data[key] = value.split('|').map(url => url.trim());
    } else if (key === 'artist' || key === 'romanized-artist') {
      data[key] = value.split(',').map(a => a.trim());
    } else if (key === 'title' || key === 'romanized-title' || key === 'album') {
      data[key] = value;
    } else if (key === 'lyrics') {
      data[key] = value;
      const lrcFile = path.resolve(path.dirname(filePath), value);
      if (!fs.existsSync(lrcFile)) {
        warnings.push(`[${fileName}] lyrics file '${value}' missing.`);
      }
    } else {
      errors.push(`[${fileName}:${lineNum}] unidentified metadata found -> '${line}'`);
    }
  });

  if (trackIdentity && !identified) {
    const title = data['romanized-title'] || data['title'];
    const artist = data['romanized-artist'] || data['artist'];
    if (title && artist) {
      trackIdentity(title, artist);
      identified = true;
    }
  }

  const keysPresent = new Set(Object.keys(data));
  const missing = Array.from(REQUIRED).filter(k => !keysPresent.has(k));

  if (missing.length > 0) {
    errors.push(`[${fileName}] missing required parameter(s): ${missing.join(', ')}`);
  }

  if (errors.length > 0) {
    if (!silent) {
      console.log('\x1b[1;31m[-] status: FAILED\x1b[0m');
      errors.forEach(err => console.log(`\x1b[1;31m• [E] ${err}\x1b[0m`));
    }
    return null;
  }

  if (!silent) {
    console.log('\x1b[1;32m[+] status: PASSED\x1b[0m');
    warnings.forEach(warn => console.log(`\x1b[1;33m• [!] ${warn}\x1b[0m`));

    console.log('\n\x1b[1;36m[+] parsed metadata:\x1b[0m');
    console.log(data);
  }

  return data;
}

export function _track_identify(fileName: string): TrackIdentity | null {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const filePath = path.resolve(currentDir, fileName);
  const fileExt = path.extname(fileName);

  if (!fs.existsSync(filePath) || fileExt !== '.mdata') {
    return null;
  }

  const track: TrackIdentity = {};
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split(/\r?\n/);

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line || !(line.startsWith('[') && line.endsWith(']')) || !line.includes(':')) {
      continue;
    }

    const innerContent = line.slice(1, -1).trim();
    const colonIdx = innerContent.indexOf(':');
    const key = innerContent.slice(0, colonIdx).trim().toLowerCase();
    const value = innerContent.slice(colonIdx + 1).trim();

    if (key === 'artist' || key === 'romanized-artist') {
      track.artist = value.split(',').map((a: string) => a.trim());
    } else if (key === 'title' || key === 'romanized-title') {
      track.title = value;
    } else if (key === 'explicit') {
      if (!['true', 'false'].includes(value.toLowerCase())) {
        continue;
      }
      track.explicit = value.toLowerCase();
    }
  }

  return track;
}

export function prompt(query: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise(resolve => {
    rl.question(query, (ans: string) => {
      rl.close();
      resolve(ans);
    });
  });
}

export async function multi_file_input(): Promise<void> {
  const files: string[] = [];
  console.log('\nenter file names (or hit Enter to finish)');
  while (true) {
    const file = await prompt('\x1b[1;38;2;12;59;5m[?] .mdata file to parse -> \x1b[0m');
    if (file === '') {
      break;
    }
    files.push(file);
  }

  for (const mdata_file of files) {
    validateMdata(mdata_file);
  }
}

export async function single_file_input(): Promise<void> {
  const file = await prompt('\x1b[1;38;2;12;59;5m[?] .mdata file to parse -> \x1b[0m');
  validateMdata(file);
}

// for systems that have to programmically pass files without user input
export function singlefile(file: string, silent: boolean = false): MDataResult | null {
  return validateMdata(file, silent);
}

export function multifile(...files: string[]): (MDataResult | null)[] {
  return files.map(file => validateMdata(file));
}

export function singletrack_identity(file: string): void {
  const identity = _track_identify(file);
  if (!identity) return;

  console.log(`\x1b[1m[${file}] track info:\x1b[0m`);
  console.log(`- title: \x1b[1m${identity.title}\x1b[0m`);
  console.log(`- artist(s): \x1b[1m${identity.artist?.join(', ')}\x1b[0m`);
  console.log(`- explicit: \x1b[1m${identity.explicit}\x1b[0m`);
}

export function multitrack_identify(...files: string[]): void {
  for (const file of files) {
    singletrack_identity(file);
  }
}

export function singlefile_autoname(file: string): void {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const filePath = path.resolve(currentDir, file);
  const identity = _track_identify(file);

  if (!identity || !identity.title || !identity.artist) {
    return;
  }

  const title = identity.title;
  const artists = Array.isArray(identity.artist) ? identity.artist.join(', ') : identity.artist;

  const tempTitle = title.replace(/[^\w\s]/g, '');
  const filetitle = tempTitle.trim().replace(/\s+/g, '_');

  const tempArtists = artists.replace(/[^\w\s]/g, '');
  const fileartists = tempArtists.trim().replace(/\s+/g, '_');

  const fullfile = `${filetitle.toLowerCase()}-${fileartists.toLowerCase()}.mdata`;
  const newFile = path.resolve(path.dirname(filePath), fullfile);

  fs.renameSync(filePath, newFile);
}

export function multifile_autoname(...files: string[]): void {
  for (const file of files) {
    singlefile_autoname(file);
  }
}

function getMdataFiles(dirPath: string, recursive: boolean): string[] {
  let results: string[] = [];
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory() && recursive) {
      results = results.concat(getMdataFiles(fullPath, recursive));
    } else if (entry.isFile() && entry.name.endsWith('.mdata')) {
      results.push(fullPath);
    }
  }
  return results;
}

export function directory_mdata(dirPath: string = '.', recursive: boolean = false, silent: boolean = false): (MDataResult | null)[] {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const targetDir = path.resolve(currentDir, dirPath);

  if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
    if (!silent) {
      console.log(`\x1b[1;31m[-] directory '${dirPath}' not found.\x1b[0m`);
    }
    return [];
  }

  const mdataFiles = getMdataFiles(targetDir, recursive).map(f => path.relative(currentDir, f));

  if (mdataFiles.length === 0 && !silent) {
    console.log(`\x1b[1;33m[!] no .mdata files found in '${dirPath}'.\x1b[0m`);
    return [];
  }

  return mdataFiles.map(file => validateMdata(file, silent));
}

export function directory_autoname(dirPath: string = '.', recursive: boolean = false): void {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const targetDir = path.resolve(currentDir, dirPath);

  if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
    console.log(`\x1b[1;31m[-] directory '${dirPath}' not found.\x1b[0m`);
    return;
  }

  const mdataFiles = getMdataFiles(targetDir, recursive).map(f => path.relative(currentDir, f));
  for (const filePath of mdataFiles) {
    singlefile_autoname(filePath);
  }
}

export async function main(): Promise<void> {
  while (true) {
    console.log('\x1b[1mselect mode:\x1b[0m');
    console.log('1. single file');
    console.log('2. multiple files');
    console.log('3. entire folder');

    const mode = (await prompt('\x1b[1;38;2;12;59;5m[?] option (1/2/3) -> \x1b[0m')).trim();

    if (mode === '1') {
      await single_file_input();
      break;
    } else if (mode === '2') {
      await multi_file_input();
      break;
    } else if (mode === '3') {
      const folderInput = await prompt('\x1b[1;38;2;12;59;5m[?] folder path (leave empty for current dir) -> \x1b[0m');
      const folder = folderInput.trim() || '.';
      const recInput = await prompt('\x1b[1;38;2;12;59;5m[?] include subfolders? (y/n) -> \x1b[0m');
      const rec = recInput.trim().toLowerCase().startsWith('y');
      directory_mdata(folder, rec);
      break;
    } else {
      console.log('\x1b[1;33m[!] invalid option.\x1b[0m\n');
    }
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}