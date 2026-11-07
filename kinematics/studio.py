"""Session-owned course drafts and private, unprocessed document uploads."""
import hashlib
import io
import json
import secrets
import time
import zipfile
from pathlib import Path

KINDS = {'lecture', 'practice', 'past_exam', 'solution', 'supplement'}
MAX_UPLOAD = 25 * 1024 * 1024


class StudioError(ValueError):
    pass


class Studio:
    def __init__(self, store, directory):
        self.store = store
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        with store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS courses (id TEXT PRIMARY KEY, owner TEXT NOT NULL, payload TEXT NOT NULL)')
            db.execute('CREATE INDEX IF NOT EXISTS course_owner ON courses(owner)')
            db.execute('CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, course TEXT NOT NULL, payload TEXT NOT NULL)')

    def list(self, owner):
        if getattr(self.store,'auth',None):self.store.auth.require_admin(owner)
        with self.store.connect() as db:
            rows = db.execute('SELECT payload FROM courses WHERE owner=? ORDER BY rowid DESC', (owner,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def get(self, owner, course):
        if getattr(self.store,'auth',None):self.store.auth.require_admin(owner)
        with self.store.connect() as db:
            row = db.execute('SELECT payload FROM courses WHERE id=? AND owner=?', (course, owner)).fetchone()
            if not row:
                raise StudioError('Course not found in this workspace.')
            documents = db.execute('SELECT payload FROM documents WHERE course=? ORDER BY rowid DESC', (course,)).fetchall()
        return json.loads(row[0]) | {'documents': [json.loads(r[0]) for r in documents]}

    def create(self, owner, data):
        if getattr(self.store,'auth',None):self.store.auth.require_admin(owner)
        def text(key, default, maximum):
            value = data.get(key, default)
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise StudioError(f'Enter a valid {key} (up to {maximum} characters).')
            return value.strip()
        description = data.get('description', '')
        if not isinstance(description, str) or len(description) > 2000:
            raise StudioError('Description must be under 2,000 characters.')
        course = {'id': secrets.token_hex(12), 'title': text('title', '', 100),
                  'code': text('code', 'PHYS-101', 30), 'language': text('language', 'English', 50),
                  'description': description.strip(), 'status': 'draft', 'created': time.time()}
        with self.store.connect() as db:
            db.execute('INSERT INTO courses VALUES (?,?,?)', (course['id'], owner, json.dumps(course)))
        return course | {'documents': []}

    def upload(self, owner, course, filename, kind, contains_solutions, body):
        self.get(owner, course)
        if kind not in KINDS:
            raise StudioError('Choose a supported document category.')
        if not filename or len(filename) > 180 or any(c in filename for c in '/\\\0') or any(ord(c) < 32 for c in filename):
            raise StudioError('Use a plain document filename without folder paths.')
        suffix = Path(filename).suffix.lower()
        if suffix not in {'.pdf', '.pptx'}:
            raise StudioError('Upload a PDF or PowerPoint (.pptx) document.')
        if not body or len(body) > MAX_UPLOAD:
            raise StudioError('Each document must be between 1 byte and 25 MB.')
        if suffix == '.pdf' and not body.startswith(b'%PDF-'):
            raise StudioError('This file does not have a valid PDF header.')
        if suffix == '.pptx':
            try:
                with zipfile.ZipFile(io.BytesIO(body)) as archive:
                    names = archive.namelist()
                    if '[Content_Types].xml' not in names or 'ppt/presentation.xml' not in names:
                        raise StudioError('This is not a PowerPoint presentation.')
                    if sum(x.file_size for x in archive.infolist()) > 250 * 1024 * 1024:
                        raise StudioError('The expanded presentation is too large.')
            except zipfile.BadZipFile:
                raise StudioError('The PowerPoint file is not a valid archive.')
        digest = hashlib.sha256(body).hexdigest()
        existing = self.get(owner, course)['documents']
        if any(d['sha256'] == digest for d in existing):
            raise StudioError('This exact document is already in the course.')
        record = {'id': secrets.token_hex(16), 'filename': filename, 'kind': kind,
                  'contains_solutions': bool(contains_solutions or kind == 'solution'), 'bytes': len(body),
                  'sha256': digest, 'status': 'stored_pending_review', 'created': time.time()}
        file = self.directory / (record['id'] + suffix)
        try:
            with file.open('xb') as output:
                output.write(body)
            file.chmod(0o600)
            with self.store.connect() as db:
                db.execute('INSERT INTO documents VALUES (?,?,?)', (record['id'], course, json.dumps(record)))
        except Exception:
            file.unlink(missing_ok=True)
            raise
        return record

    def classify(self, owner, course, document, data):
        current = self.get(owner, course)
        record = next((d for d in current['documents'] if d['id'] == document), None)
        if not record:
            raise StudioError('Document not found.')
        if data.get('kind') not in KINDS or not isinstance(data.get('contains_solutions'), bool):
            raise StudioError('Select a category and solution-access status.')
        record.update(kind=data['kind'], contains_solutions=data['contains_solutions'] or data['kind'] == 'solution')
        with self.store.connect() as db:
            db.execute('UPDATE documents SET payload=? WHERE id=? AND course=?', (json.dumps(record), document, course))
        return record
