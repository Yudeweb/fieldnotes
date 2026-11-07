"""Local accounts, one privately provisioned administrator, and revocable sessions."""
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from pathlib import Path

SESSION_SECONDS = 14 * 24 * 60 * 60


class AuthError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    value = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=32768,
                           r=8, p=1, maxmem=64*1024*1024).hex()
    return f'scrypt:{salt}:{value}'


def password_matches(password, encoded):
    if not isinstance(password, str) or len(password) > 128:
        return False
    return hmac.compare_digest(password_hash(password, encoded.split(':')[1]), encoded)


def email_value(value):
    if not isinstance(value, str) or len(value) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value.strip()):
        raise AuthError('Enter a valid email address.')
    return value.strip().casefold()


def profile_values(data):
    name, language = data.get('name', ''), data.get('language', 'English')
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
        raise AuthError('Enter your name (up to 80 characters).')
    if not isinstance(language, str) or not 1 <= len(language.strip()) <= 50:
        raise AuthError('Choose an explanation language (up to 50 characters).')
    return name.strip(), language.strip()


def validate_password(value):
    if not isinstance(value, str) or not 12 <= len(value) <= 128:
        raise AuthError('Use a password of 12–128 characters.')
    return value


class Accounts:
    def __init__(self, store):
        self.store = store
        self.setup_file = Path(store.file).parent / 'admin-setup.json'
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
                password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','student')),
                language TEXT NOT NULL, created REAL NOT NULL)""")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS sole_admin ON users(role) WHERE role='admin'")
            db.execute('CREATE TABLE IF NOT EXISTS auth_sessions (token TEXT PRIMARY KEY, user TEXT NOT NULL, expires REAL NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS auth_settings (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS auth_attempts (scope TEXT, created REAL)')
            db.execute('CREATE INDEX IF NOT EXISTS auth_attempt_scope ON auth_attempts(scope,created)')
            db.execute('BEGIN IMMEDIATE')
            admin = db.execute("SELECT id FROM users WHERE role='admin'").fetchone()
            setup = db.execute("SELECT value FROM auth_settings WHERE key='setup_hash'").fetchone()
            if not admin and not setup:
                token = json.loads(self.setup_file.read_text())['token'] if self.setup_file.exists() else secrets.token_urlsafe(32)
                # The plaintext setup credential is only in an ignored, owner-readable file.
                if not self.setup_file.exists():
                    with open(self.setup_file, 'x', opener=lambda p, f: os.open(p, f, 0o600)) as output:
                        json.dump({'token': token}, output)
                self.setup_file.chmod(0o600)
                db.execute("INSERT INTO auth_settings VALUES ('setup_hash',?)", (self.token_hash(token),))
        if admin:
            self.setup_file.unlink(missing_ok=True)
        self.dummy_password = password_hash(secrets.token_urlsafe(32))

    @staticmethod
    def token_hash(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def public(row):
        return dict(zip(('id','email','name','role','language','created'), row)) if row else None

    def user(self, id):
        with self.store.connect() as db:
            row = db.execute('SELECT id,email,name,role,language,created FROM users WHERE id=?', (id,)).fetchone()
        return self.public(row)

    def current(self, token_hash):
        with self.store.connect() as db:
            row = db.execute('SELECT u.id,u.email,u.name,u.role,u.language,u.created FROM auth_sessions s JOIN users u ON u.id=s.user WHERE s.token=? AND s.expires>?', (token_hash,time.time())).fetchone()
        return self.public(row)

    def require_admin(self, owner):
        user = self.user(owner)
        if not user or user['role'] != 'admin':
            raise AuthError('Only the administrator can access this workspace.', 403)
        return user

    def limit(self, operation, peer, email=''):
        now = time.time()
        scopes = [(f'{operation}:ip:{peer}', 60)]
        if email:
            scopes.append((f'{operation}:email:{self.token_hash(email)}', 10))
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM auth_attempts WHERE created<?', (now-900,))
            for scope, cap in scopes:
                if db.execute('SELECT COUNT(*) FROM auth_attempts WHERE scope=?', (scope,)).fetchone()[0] >= cap:
                    raise AuthError('Too many attempts. Please try again in 15 minutes.', 429)
            db.executemany('INSERT INTO auth_attempts VALUES (?,?)', [(s,now) for s,_ in scopes])

    def new_session(self, db, user, previous=None):
        token = secrets.token_hex(32)
        db.execute('DELETE FROM auth_sessions WHERE expires<?', (time.time(),))
        if previous:
            db.execute('DELETE FROM auth_sessions WHERE token=?', (previous,))
        db.execute('INSERT INTO auth_sessions VALUES (?,?,?)', (self.token_hash(token),user,time.time()+SESSION_SECONDS))
        return token

    def register(self, data, previous):
        email = email_value(data.get('email'))
        name, language = profile_values(data)
        hashed = password_hash(validate_password(data.get('password')))
        id = secrets.token_hex(16)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM users WHERE email=?', (email,)).fetchone():
                raise AuthError('This email is already registered. Sign in instead.')
            # Never accept a role, reviewer flag, owner ID or permissions from registration.
            db.execute("INSERT INTO users VALUES (?,?,?,?,'student',?,?)", (id,email,name,hashed,language,time.time()))
            token = self.new_session(db,id,previous)
        return self.user(id), token

    def setup(self, data, previous):
        secret = data.get('token', '')
        if not isinstance(secret, str) or len(secret) > 200:
            raise AuthError('Invalid administrator setup link.',403)
        name, language = profile_values(data)
        email = email_value(data.get('email'))
        hashed = password_hash(validate_password(data.get('password')))
        id = secrets.token_hex(16)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            setup = db.execute("SELECT value FROM auth_settings WHERE key='setup_hash'").fetchone()
            if db.execute("SELECT 1 FROM users WHERE role='admin'").fetchone() or not setup or not hmac.compare_digest(setup[0], self.token_hash(secret)):
                raise AuthError('This administrator setup link is invalid or has already been used.',403)
            if db.execute('SELECT 1 FROM users WHERE email=?',(email,)).fetchone():
                raise AuthError('Use an email that has not been registered as a student.')
            db.execute("INSERT INTO users VALUES (?,?,?,?,'admin',?,?)",(id,email,name,hashed,language,time.time()))
            # Transfer the previous local demonstration's authoring workspace to its sole admin.
            db.execute('UPDATE courses SET owner=? WHERE owner NOT IN (SELECT id FROM users)', (id,))
            db.execute("UPDATE agent_records SET owner=? WHERE owner NOT IN (SELECT id FROM users) AND (course<>'' OR kind IN ('rubric','resource','curation','clarification','dispute'))", (id,))
            db.execute("UPDATE agent_jobs SET owner=? WHERE owner NOT IN (SELECT id FROM users) AND role IN ('source_reader','builder_structure','builder_content','curator','scout')", (id,))
            # Only the owner's current old browser contributes personal progress and history.
            db.execute('UPDATE state SET session=? WHERE session=?', (id,previous))
            for table in ('ai_runs','agent_records','agent_jobs','cohort_signals','resource_votes','study_time'):
                db.execute(f'UPDATE {table} SET owner=? WHERE owner=?', (id,previous))
            db.execute("INSERT OR REPLACE INTO agent_settings VALUES ('reviewer',?)", (id,))
            db.execute("DELETE FROM auth_settings WHERE key='setup_hash'")
            token = self.new_session(db,id,previous)
        self.setup_file.unlink(missing_ok=True)
        return self.user(id), token

    def login(self, data, previous):
        email = email_value(data.get('email'))
        with self.store.connect() as db:
            row = db.execute('SELECT id,password FROM users WHERE email=?', (email,)).fetchone()
        valid = password_matches(data.get('password'), row[1] if row else self.dummy_password)
        if not row or not valid:
            raise AuthError('Email or password is incorrect.',401)
        with self.store.connect() as db:
            token = self.new_session(db,row[0],previous)
        return self.user(row[0]), token

    def logout(self, token_hash):
        with self.store.connect() as db:
            db.execute('DELETE FROM auth_sessions WHERE token=?',(token_hash,))

    def update(self, owner, data):
        name, language = profile_values(data)
        with self.store.connect() as db:
            db.execute('UPDATE users SET name=?,language=? WHERE id=?',(name,language,owner))
        return self.user(owner)

    def change_password(self, owner, data):
        with self.store.connect() as db:
            current = db.execute('SELECT password FROM users WHERE id=?',(owner,)).fetchone()
        if not current or not password_matches(data.get('current_password'),current[0]):
            raise AuthError('Your current password is incorrect.',403)
        encoded = password_hash(validate_password(data.get('password')))
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('UPDATE users SET password=? WHERE id=? AND password=?',(encoded,owner,current[0])).rowcount!=1:
                raise AuthError('Your password changed in another session. Sign in again.',403)
            db.execute('DELETE FROM auth_sessions WHERE user=?',(owner,))
            token = self.new_session(db,owner)
        return token

    def students(self):
        with self.store.connect() as db:
            rows = db.execute("SELECT id,email,name,role,language,created FROM users WHERE role='student' ORDER BY created DESC").fetchall()
        return [self.public(row) for row in rows]
