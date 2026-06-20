import { useEffect } from "react";
import api from "../services/api/api";
import { localStorageManualLogout } from "../utils/constants";
import { useAuthStore, type AuthState } from "../store/useAuthStore";
import { useLoadingStore, type LoadingState } from "../store/useLoadingStore";

export const useAuthInitializer = () => {
  const setUserId = useAuthStore((state: AuthState) => state.setUserId);
  const setIsLoading = useLoadingStore(
    (state: LoadingState) => state.setIsLoading,
  );

  useEffect(() => {
    const initAuth = async () => {
      const isManuallyLoggedOut =
        localStorage.getItem(localStorageManualLogout) === "true";

      if (isManuallyLoggedOut) {
        setIsLoading(false);
        return;
      }

      try {
        const res = await api.get("/me", { skipAuthInterceptor: true });
        setUserId(res.data.user_id);
      } catch {
        console.log("User not logged in");
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, [setUserId, setIsLoading]);
};
