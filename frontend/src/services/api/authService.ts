import api from "./api";
import type { LoginFormInputs } from "../../utils/interfaces";
import type { RegisterFormInputs } from "../../utils/schemas";

export const login = async (data: LoginFormInputs): Promise<number> => {
  const res = await api.post("/auth/login", data);
  return res.data?.user_id;
};

export const googleLogin = async (token?: string): Promise<number> => {
  const res = await api.post(
    "/auth/google",
    { token },
    { skipAuthInterceptor: true },
  );
  return res.data?.user_id;
};

export const registerUser = async (
  data: RegisterFormInputs,
): Promise<number> => {
  const res = await api.post("/auth/register", data);
  return res.data?.user_id;
};

export const logoutUser = (): Promise<void> => {
  return api.post("/auth/logout");
};
