import express, { Request, Response } from 'express';
import multer from 'multer';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { validateMdata, _track_identify } from './mdata.js';

const app = express();
const upload = multer({ dest: os.tmpdir() });

app.use(express.json());

app.post('/parse/file', upload.single('file'), (req: Request, res: Response): void => {
  if (!req.file) {
    res.status(400).json({ error: 'No file uploaded' });
    return;
  }

  const tmpPath = req.file.path;
  const targetPath = `${tmpPath}.mdata`;

  try {
    fs.renameSync(tmpPath, targetPath);
    const result = validateMdata(targetPath, true);

    if (!result) {
      res.status(422).json({ error: 'Invalid .mdata file content or syntax' });
      return;
    }

    res.json({ status: 'success', data: result });
  } finally {
    if (fs.existsSync(targetPath)) fs.unlinkSync(targetPath);
    if (fs.existsSync(tmpPath)) fs.unlinkSync(tmpPath);
  }
});

app.post('/parse/raw', (req: Request, res: Response): void => {
  const { content } = req.body;
  if (!content || typeof content !== 'string') {
    res.status(400).json({ error: 'Missing string body field "content"' });
    return;
  }

  const tmpPath = path.join(os.tmpdir(), `raw_${Date.now()}.mdata`);

  try {
    fs.writeFileSync(tmpPath, content, 'utf-8');
    const result = validateMdata(tmpPath, true);

    if (!result) {
      res.status(422).json({ error: 'Invalid .mdata content or syntax' });
      return;
    }

    res.json({ status: 'success', data: result });
  } finally {
    if (fs.existsSync(tmpPath)) fs.unlinkSync(tmpPath);
  }
});

app.post('/identify/file', upload.single('file'), (req: Request, res: Response): void => {
  if (!req.file) {
    res.status(400).json({ error: 'No file uploaded' });
    return;
  }

  const tmpPath = req.file.path;
  const targetPath = `${tmpPath}.mdata`;

  try {
    fs.renameSync(tmpPath, targetPath);
    const identity = _track_identify(targetPath);

    if (!identity) {
      res.status(422).json({ error: 'Unable to extract track identity' });
      return;
    }

    res.json({ status: 'success', identity });
  } finally {
    if (fs.existsSync(targetPath)) fs.unlinkSync(targetPath);
    if (fs.existsSync(tmpPath)) fs.unlinkSync(tmpPath);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`[+] TS API server running on http://localhost:${PORT}`);
});