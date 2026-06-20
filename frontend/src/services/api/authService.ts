import api from "./api";
import type {
  LoginFormInputs,
  RegisterFormInputs,
} from "../../utils/interfaces";

export const login = async (data: LoginFormInputs): Promise<number> => {
  const res = await api.post("/auth/login", data);
  return res.data?.user_id;
};

export const registerUser = async (
  data: RegisterFormInputs,
): Promise<number> => {
  const res = await api.post("/auth/register", data);
  return res.data?.user_id;
};

export const logoutUser = () => {
  return api.post("/auth/logout");
};
