import { useEffect } from "react";
import api from "../services/api/api";
import { useAuthStore } from "../store/useAuthStore";
import { useLoadingStore } from "../store/useLoadingStore";

export const useAuthInitializer = () => {
  const setUserId = useAuthStore((state) => state.setUserId);
  const setIsLoading = useLoadingStore((state) => state.setIsLoading);

  useEffect(() => {
    const initAuth = async () => {
      const isManuallyLoggedOut =
        localStorage.getItem("auth_manual_logout") === "true";

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
