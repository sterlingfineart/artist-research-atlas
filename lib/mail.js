'use strict';
/*
 * Outbound mail for the Feedback page: a minimal SMTP client on Node
 * built-ins only (the Atlas server is zero-dependency, so no mail
 * library). Configuration comes from the environment:
 *
 *   FEEDBACK_SMTP_HOST  — required; without it mail is "not configured"
 *   FEEDBACK_SMTP_PORT  — default 587; port 465 means implicit TLS,
 *                         otherwise STARTTLS is used when offered
 *   FEEDBACK_SMTP_USER / FEEDBACK_SMTP_PASS — when both are set, AUTH
 *                         (PLAIN if offered, else LOGIN) is performed
 *   FEEDBACK_FROM       — From address; defaults to the SMTP user
 *   FEEDBACK_TO         — recipient; defaults to the Atlas editor
 *
 * The credentials live only in the server environment (on Render, the
 * service's environment variables) — never in this repository.
 */
const net = require('net');
const tls = require('tls');

const TO_DEFAULT = 'john@sterlingfineart.com';

function config() {
  const host = (process.env.FEEDBACK_SMTP_HOST || '').trim();
  if (!host) return null;
  const port = parseInt(process.env.FEEDBACK_SMTP_PORT || '587', 10) || 587;
  const user = (process.env.FEEDBACK_SMTP_USER || '').trim();
  const pass = process.env.FEEDBACK_SMTP_PASS || '';
  return {
    host,
    port,
    user,
    pass,
    from: (process.env.FEEDBACK_FROM || '').trim() || user,
    to: (process.env.FEEDBACK_TO || '').trim() || TO_DEFAULT,
  };
}

const configured = () => !!config();

/* One SMTP conversation: buffers the socket, assembles multi-line
 * replies ("250-..." until "250 ...") and hands them to the reader. */
class Session {
  constructor(socket) {
    this.socket = socket;
    this.buf = '';
    this.lines = [];
    this.ready = [];
    this.waiter = null;
    this.error = null;
    socket.setTimeout(20000);
    this._onData = (d) => this._data(d);
    this._onError = (e) => this._fail(e);
    this._onClose = () => this._fail(new Error('SMTP connection closed'));
    this._onTimeout = () => { this._fail(new Error('SMTP timed out')); socket.destroy(); };
    socket.on('data', this._onData);
    socket.on('error', this._onError);
    socket.on('close', this._onClose);
    socket.on('timeout', this._onTimeout);
  }
  detach() {
    this.socket.removeListener('data', this._onData);
    this.socket.removeListener('error', this._onError);
    this.socket.removeListener('close', this._onClose);
    this.socket.removeListener('timeout', this._onTimeout);
  }
  _data(d) {
    this.buf += d.toString('utf8');
    let i;
    while ((i = this.buf.indexOf('\r\n')) >= 0) {
      const line = this.buf.slice(0, i);
      this.buf = this.buf.slice(i + 2);
      this.lines.push(line);
      if (/^\d{3}( |$)/.test(line)) {
        const resp = { code: parseInt(line.slice(0, 3), 10), lines: this.lines };
        this.lines = [];
        if (this.waiter) { const w = this.waiter; this.waiter = null; w.resolve(resp); }
        else this.ready.push(resp);
      }
    }
  }
  _fail(e) {
    if (!this.error) this.error = e;
    if (this.waiter) { const w = this.waiter; this.waiter = null; w.reject(e); }
  }
  read() {
    if (this.ready.length) return Promise.resolve(this.ready.shift());
    if (this.error) return Promise.reject(this.error);
    return new Promise((resolve, reject) => { this.waiter = { resolve, reject }; });
  }
  async cmd(line, ...expect) {
    this.socket.write(line + '\r\n');
    const r = await this.read();
    if (expect.length && !expect.includes(r.code)) {
      throw new Error(`SMTP ${line.split(' ')[0]} refused: ${r.code} ${r.lines.join(' | ')}`);
    }
    return r;
  }
}

function connect(cfg) {
  return new Promise((resolve, reject) => {
    const sock = cfg.port === 465
      ? tls.connect({ host: cfg.host, port: cfg.port, servername: cfg.host })
      : net.connect({ host: cfg.host, port: cfg.port });
    sock.once('error', reject);
    sock.once(cfg.port === 465 ? 'secureConnect' : 'connect', () => resolve(sock));
  });
}

function capabilities(ehloResp) {
  return ehloResp.lines.map((l) => l.slice(4).trim().toUpperCase());
}

function encodeHeader(s) {
  // RFC 2047 encoded-word when the value leaves printable ASCII.
  return /[^\x20-\x7e]/.test(s) ? `=?UTF-8?B?${Buffer.from(s, 'utf8').toString('base64')}?=` : s;
}

function buildMessage(cfg, { name, email, comments, wishes }) {
  const headers = [
    `From: ${cfg.from}`,
    `To: ${cfg.to}`,
    ...(email ? [`Reply-To: ${email}`] : []),
    `Subject: ${encodeHeader('Artist Research Atlas — feedback')}`,
    `Date: ${new Date().toUTCString()}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=utf-8',
    'Content-Transfer-Encoding: base64',
  ];
  const parts = ['Feedback sent from the Artist Research Atlas website.', ''];
  parts.push(`Name: ${name || '—'}`);
  parts.push(`Email: ${email || '—'}`);
  if (comments) parts.push('', 'Comments:', comments);
  if (wishes) parts.push('', 'What else would you like to see on the site?', wishes);
  const b64 = Buffer.from(parts.join('\n'), 'utf8').toString('base64');
  const body = (b64.match(/.{1,76}/g) || []).join('\r\n');
  return headers.join('\r\n') + '\r\n\r\n' + body + '\r\n';
}

/* Send one feedback message. Resolves only once the receiving server
 * has accepted the message body (final 250 after DATA); throws on any
 * refusal, so the caller can answer honestly. */
async function sendFeedback(fields) {
  const cfg = config();
  if (!cfg) throw new Error('mail not configured');
  if (!cfg.from) throw new Error('no From address (set FEEDBACK_FROM or FEEDBACK_SMTP_USER)');
  const sock = await connect(cfg);
  let s = new Session(sock);
  try {
    const greeting = await s.read();
    if (greeting.code !== 220) throw new Error(`SMTP greeting refused: ${greeting.code}`);
    let caps = capabilities(await s.cmd('EHLO localhost', 250));
    if (cfg.port !== 465 && caps.some((c) => c === 'STARTTLS')) {
      await s.cmd('STARTTLS', 220);
      s.detach();
      const secure = tls.connect({ socket: sock, servername: cfg.host });
      await new Promise((resolve, reject) => { secure.once('secureConnect', resolve); secure.once('error', reject); });
      s = new Session(secure);
      caps = capabilities(await s.cmd('EHLO localhost', 250));
    }
    if (cfg.user && cfg.pass) {
      const auth = caps.find((c) => c.startsWith('AUTH '));
      const mechs = auth ? auth.slice(5).split(/\s+/) : [];
      if (mechs.includes('PLAIN')) {
        await s.cmd('AUTH PLAIN ' + Buffer.from(`\0${cfg.user}\0${cfg.pass}`, 'utf8').toString('base64'), 235);
      } else {
        await s.cmd('AUTH LOGIN', 334);
        await s.cmd(Buffer.from(cfg.user, 'utf8').toString('base64'), 334);
        await s.cmd(Buffer.from(cfg.pass, 'utf8').toString('base64'), 235);
      }
    }
    await s.cmd(`MAIL FROM:<${cfg.from}>`, 250);
    await s.cmd(`RCPT TO:<${cfg.to}>`, 250, 251);
    await s.cmd('DATA', 354);
    s.socket.write(buildMessage(cfg, fields) + '.\r\n');
    const done = await s.read();
    if (done.code !== 250) throw new Error(`SMTP message refused: ${done.code} ${done.lines.join(' | ')}`);
    try { await s.cmd('QUIT', 221); } catch { /* accepted already; a lost goodbye is harmless */ }
  } finally {
    s.socket.end();
    s.socket.destroy();
  }
}

module.exports = { configured, sendFeedback, TO_DEFAULT };
