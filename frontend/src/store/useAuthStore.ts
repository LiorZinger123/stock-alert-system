import { create } from "zustand";

interface AuthState {
  userId: number | null;
  setUserId: (id: number | null) => void;
  clearUser: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  userId: null,
  setUserId: (id: number | null) => set({ userId: id }),
  clearUser: () => set({ userId: null }),
}));
