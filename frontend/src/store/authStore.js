import { create } from "zustand";

const TOKEN_KEY = "cloud_log_token";
const ROLE_KEY = "cloud_log_role";
const USERNAME_KEY = "cloud_log_username";

function decodeJwtPayload(token) {
  try {
    const payload = token.split(".")[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(normalized);
    return JSON.parse(json);
  } catch {
    return {};
  }
}

export const authStore = create((set) => ({
  token: localStorage.getItem(TOKEN_KEY) || "",
  role: localStorage.getItem(ROLE_KEY) || "",
  username: localStorage.getItem(USERNAME_KEY) || "",

  signIn: (token) => {
    const payload = decodeJwtPayload(token);
    const role = payload.role || "viewer";
    const username = payload.sub || "";

    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(ROLE_KEY, role);
    localStorage.setItem(USERNAME_KEY, username);

    set({ token, role, username });
  },

  signOut: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(USERNAME_KEY);

    set({ token: "", role: "", username: "" });
  },
}));
