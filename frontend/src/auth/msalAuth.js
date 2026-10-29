// frontend/src/auth/msalAuth.js
// Modul Khusus Autentikasi Microsoft Entra ID (SSO) di Frontend Vue 3
import { PublicClientApplication, InteractionRequiredAuthError } from '@azure/msal-browser';

export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID || 'a8f412c0-3b91-4e7a-9c1d-55f802e19a11',
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID || '72f988bf-86f1-41af-91ab-2d7cd011db47'}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

export const loginScopes = {
  scopes: ['openid', 'profile', 'email', 'User.Read', `api://${msalConfig.auth.clientId}/Issues.Manage`],
};

export const msalInstance = new PublicClientApplication(msalConfig);

export async function initializeMsal() {
  await msalInstance.initialize();
  await msalInstance.handleRedirectPromise();
}

export async function signInWithMicrosoftPopup() {
  const response = await msalInstance.loginPopup(loginScopes);
  msalInstance.setActiveAccount(response.account);
  return response.account;
}

export async function acquireBearerToken() {
  const account = msalInstance.getActiveAccount() || msalInstance.getAllAccounts()[0];
  if (!account) return null;
  try {
    const tokenRes = await msalInstance.acquireTokenSilent({ ...loginScopes, account });
    return tokenRes.accessToken;
  } catch (err) {
    if (err instanceof InteractionRequiredAuthError) {
      const tokenRes = await msalInstance.acquireTokenPopup(loginScopes);
      return tokenRes.accessToken;
    }
    throw err;
  }
}