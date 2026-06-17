import api from "./api";
import type { LoginFormInputs, RegisterFormInputs } from "../../utils/interfaces";

export const login = (data: LoginFormInputs) => {
    return api.post("/auth/login", data);
};

export const registerUser = (data: RegisterFormInputs) => {
    return api.post("/auth/register", data);
}

export const logoutUser = () => {
    return api.post("/auth/logout");
}
