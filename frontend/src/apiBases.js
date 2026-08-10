export const SKD_API = 'https://certificate-generator2skd.onrender.com';
export const DEAD_API_HOSTS = ['certificate-generator2-1.onrender.com'];

export function resolveApiBases({ primary, secondary, legacy, isDev = false } = {}) {
  const fromEnv = [primary, secondary, legacy]
    .filter(Boolean)
    .map((url) => String(url).replace(/\/$/, ''))
    .filter((url) => !DEAD_API_HOSTS.some((h) => url.includes(h)));
  if (fromEnv.length) return fromEnv;
  if (isDev) return ['http://localhost:8000'];
  return [SKD_API];
}

export function isPersistedTemplateId(id) {
  return Number.isInteger(id) && id > 0 && id < 1e9;
}

export function getApiBases() {
  return resolveApiBases({
    primary: import.meta.env.VITE_API_URL_PRIMARY,
    secondary: import.meta.env.VITE_API_URL_SECONDARY,
    legacy: import.meta.env.VITE_API_URL,
    isDev: import.meta.env.DEV,
  });
}

export function getPrimaryApiUrl() {
  return getApiBases()[0];
}

export async function fetchWithFallback(path, options = {}) {
  const bases = getApiBases();
  let lastError = null;
  let lastBad = null;
  for (const base of bases) {
    try {
      const response = await fetch(`${base}${path}`, options);
      if (response.ok) return response;
      lastBad = response;
      if (response.status === 404 && bases.length > 1) continue;
      return response;
    } catch (error) {
      lastError = error;
    }
  }
  if (lastBad) return lastBad;
  if (lastError) throw lastError;
  throw new Error('All backend URLs failed');
}
