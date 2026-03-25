const API_ROOT = import.meta.env.VITE_API_BASE_URL || '';
const API_BASE_URL = `${API_ROOT}/api/v1`;

function buildQueryParams(name, language, key) {
  const params = new URLSearchParams();
  if (name?.trim()) params.set('name', name.trim());
  if (language?.trim()) params.set('language', language.trim());
  if (key?.trim()) params.set('key', key.trim());
  return params.toString();
}

async function readError(response, fallbackMessage) {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === 'string') return payload.detail;
    if (typeof payload?.message === 'string') return payload.message;
  } catch {
    // Response body is not JSON
  }
  return fallbackMessage;
}

export async function fetchDailyVerse({ name = '', language = 'Korean', key = '' } = {}) {
  const query = buildQueryParams(name, language, key);
  const endpoint = query ? `${API_BASE_URL}/daily-verse?${query}` : `${API_BASE_URL}/daily-verse`;
  const response = await fetch(endpoint);
  if (!response.ok) throw new Error(await readError(response, 'Failed to fetch daily verse.'));
  return response.json();
}

export async function fetchCustomMessage({ name = '', situation = '', language = 'Korean', key = '' } = {}) {
  const query = buildQueryParams(name, language, key);
  const endpoint = query ? `${API_BASE_URL}/custom-message?${query}` : `${API_BASE_URL}/custom-message`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation }),
  });
  if (!response.ok) throw new Error(await readError(response, 'Failed to fetch custom message.'));
  return response.json();
}

export function normalizeVersePayload(payload) {
  if (!payload || typeof payload !== 'object') return { verse: 'No content received.', ref: 'System' };
  const verse = payload.verse || payload.message || payload.text || payload.content;
  const ref = payload.ref || payload.reference || payload.source || 'Bible';
  return {
    verse: (typeof verse === 'string' && verse.trim()) ? verse : 'No content received.',
    ref: (typeof ref === 'string' && ref.trim()) ? ref : 'Bible',
  };
}