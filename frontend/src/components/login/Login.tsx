import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import { IoEye } from "react-icons/io5";
import { IoEyeOff } from "react-icons/io5";
import { useGoogleLogin } from "@react-oauth/google";
import type { LoginFormInputs } from "../../utils/interfaces";
import { localStorageManualLogout } from "../../utils/constants";
import { googleLogin, login } from "../../services/api/authService";
import { useAuthStore, type AuthState } from "../../store/useAuthStore";
import {
  useLoadingStore,
  type LoadingState,
} from "../../store/useLoadingStore";
import './login.scss'

const Login = () => {
  const navigate = useNavigate();
  const setUserId = useAuthStore((state: AuthState) => state.setUserId);
  const { isLoading, setIsLoading } = useLoadingStore(
    (state: LoadingState) => state,
  );
  const { register, handleSubmit } = useForm<LoginFormInputs>();
  const [showPass, setShowPass] = useState<boolean>(false);

  const onSubmit = async (data: LoginFormInputs): Promise<void> => {
    try {
      setIsLoading(true);
      const userId = await login(data);
      setUserId(userId);
      navigate("/dashboard");
    } catch (err: unknown) {
      setIsLoading(false);

      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        if (status === 400) {
          toast.error("Username or password is incorrect");
        } else {
          toast.error("Failed to login, please try again");
        }
      } else {
        toast.error("An unexpected error occurred");
      }
    } finally {
      localStorage.removeItem(localStorageManualLogout);
    }
  };

  const googleLoginPopup = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        setIsLoading(true);
        const userId = await googleLogin(tokenResponse.access_token);
        setUserId(userId);
        navigate("/dashboard");
      } catch {
        toast.error("Google login failed");
      } finally {
        setIsLoading(false);
      }
    },
    onError: () => toast.error("Google login failed"),
  });

  return (
    <div className="login-register-container">
      <form id="login-form" onSubmit={handleSubmit(onSubmit)}>
        <h1 className="login-register-title">Login</h1>
        <div className="login-register-inputbox">
          <input
            id="username"
            type="text"
            required
            {...register("username", { required: true })}
          />
          <label htmlFor="username">Username</label>
        </div>
        <div className="login-register-inputbox">
          <input
            id="password"
            type={!showPass ? "password" : "text"}
            required
            {...register("password", { required: true })}
          />
          <label htmlFor="password">Password</label>
          {!showPass ? (
            <IoEye className="eye-icon" onClick={() => setShowPass(true)} />
          ) : (
            <IoEyeOff className="eye-icon" onClick={() => setShowPass(false)} />
          )}
        </div>
        <div className="login-form-buttons">
          <button
            type="submit"
            className="login-register-btn"
            disabled={isLoading}
          >
            Log in
          </button>
          <button type="button" className="google-login-btn" onClick={() => googleLoginPopup()}>
            <img src="/google-icon.jpg" alt="Google" />
            Sign in with Google
          </button>
        </div>
        <div className="login-register-link">
          <p>
            Don't have an account? <Link to="/register">Register</Link>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Login;