import api from "./api";
import type { LoginFormInputs, RegisterFormInputs } from "../utils/interfaces";

export const login = async (data: LoginFormInputs) => {
    return await api.post("/auth/login", data);
};

export const registerUser = async (data: RegisterFormInputs) => {
    return await api.post("/auth/register", data);
}