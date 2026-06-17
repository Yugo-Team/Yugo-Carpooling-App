/**
 * tokenStorage — platform-agnostic, async storage for the auth JWT.
 *
 * Goal: the same auth code runs on web (today) and on the Expo/React Native
 * mobile app (coming). The interface is intentionally ASYNC because secure
 * storage on native (expo-secure-store → iOS Keychain / Android Keystore) is
 * always async. Writing async now means the call sites don't change when the
 * native backend is swapped in.
 *
 * Platform is auto-detected at runtime:
 *   - web (a real `window.localStorage`)  → localStorage backend
 *   - React Native / Expo                 → SecureStore backend (see note below)
 *
 * MOBILE WIRING (do this when the Expo app is set up — see secureStoreBackend):
 *   1. `npx expo install expo-secure-store`
 *   2. Uncomment the dynamic import in `secureStoreBackend`.
 *
 * Interface:
 *   getToken(): Promise<string | null>
 *   setToken(token: string): Promise<void>
 *   removeToken(): Promise<void>
 */

const TOKEN_KEY = "carpool-token";

/** True when running inside React Native / Expo (no DOM `window`/`localStorage`). */
function isReactNative() {
  return (
    typeof navigator !== "undefined" &&
    navigator.product === "ReactNative"
  );
}

/** True when a usable Web Storage API is present. */
function hasLocalStorage() {
  try {
    return typeof window !== "undefined" && !!window.localStorage;
  } catch {
    return false;
  }
}

/** Web backend: synchronous localStorage wrapped in promises. */
const localStorageBackend = {
  async getToken() {
    return window.localStorage.getItem(TOKEN_KEY);
  },
  async setToken(token) {
    window.localStorage.setItem(TOKEN_KEY, token);
  },
  async removeToken() {
    window.localStorage.removeItem(TOKEN_KEY);
  },
};

/**
 * Native backend: expo-secure-store (iOS Keychain / Android Keystore).
 *
 * Left as a stub so the web build never tries to resolve `expo-secure-store`
 * (which isn't installed here). When the Expo app exists, follow MOBILE WIRING
 * above and replace the stub bodies with the commented implementation.
 */
const secureStoreBackend = {
  async getToken() {
    // const SecureStore = await import("expo-secure-store");
    // return SecureStore.getItemAsync(TOKEN_KEY);
    throw new Error(
      "secureStoreBackend not wired yet — run `npx expo install expo-secure-store` " +
        "and enable the dynamic import in tokenStorage.js"
    );
  },
  async setToken(/* token */) {
    // const SecureStore = await import("expo-secure-store");
    // return SecureStore.setItemAsync(TOKEN_KEY, token);
    throw new Error("secureStoreBackend not wired yet — see tokenStorage.js");
  },
  async removeToken() {
    // const SecureStore = await import("expo-secure-store");
    // return SecureStore.deleteItemAsync(TOKEN_KEY);
    throw new Error("secureStoreBackend not wired yet — see tokenStorage.js");
  },
};

/** Pick a backend once, at module load, based on the detected platform. */
function selectBackend() {
  if (isReactNative()) return secureStoreBackend;
  if (hasLocalStorage()) return localStorageBackend;
  // SSR / tests / unknown — no-op so imports never crash.
  return {
    async getToken() {
      return null;
    },
    async setToken() {},
    async removeToken() {},
  };
}

const backend = selectBackend();

export const tokenStorage = {
  getToken: () => backend.getToken(),
  setToken: (token) => backend.setToken(token),
  removeToken: () => backend.removeToken(),
};

export { TOKEN_KEY };
export default tokenStorage;
