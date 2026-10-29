// frontend/src/auth/oauthSession.js
// Sesi OAuth 2.0 Google/GitHub: JWT sesi internal dari backend disimpan di
// sessionStorage. Alur: tombol login -> redirect ke backend /auth/<provider>/login
// -> IdP -> callback backend -> redirect balik ke /#token=<jwt> -> disimpan di sini.

const OAUTH_TOKEN_KEY = "jiravue_oauth_token";

export function storeOAuthToken(token) {
  sessionStorage.setItem(OAUTH_TOKEN_KEY, token);
}

export function getOAuthToken() {
  return sessionStorage.getItem(OAUTH_TOKEN_KEY);
}

export function clearOAuthToken() {
  sessionStorage.removeItem(OAUTH_TOKEN_KEY);
}

export function hasOAuthSession() {
  const token = getOAuthToken();
  if (!token) return false;
  try {
    // Cek kedaluwarsa lokal (claims.exp, detik sejak epoch)
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

// Dipanggil saat App.vue mount: ambil #token=... dari URL (hasil redirect
// callback backend), simpan, lalu bersihkan fragment dari address bar.
export function consumeTokenFromUrl() {
  const hash = window.location.hash || "";
  const m = hash.match(/^#token=(.+)$/);
  if (m) {
    storeOAuthToken(m[1]);
    history.replaceState(null, "", window.location.pathname);
    return true;
  }
  return false;
}

const API_BASE =
  import.meta.env.VITE_FLASK_API_URL || "http://localhost:5001/api/v1";

export function startOAuthLogin(provider) {
  // Full-page redirect: browser pergi ke IdP via backend, balik lagi ke sini.
  window.location.href = `${API_BASE}/auth/${provider}/login`;
}
