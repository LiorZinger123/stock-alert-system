import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, type SubmitHandler } from "react-hook-form";
import axios from "axios";
import toast from "react-hot-toast";
import { IoEye } from "react-icons/io5";
import { IoEyeOff } from "react-icons/io5";
import { registerSchema } from "../../utils/schemas";
import { useAuthStore } from "../../store/useAuthStore";
import { registerUser } from "../../services/api/authService";
import { useLoadingStore } from "../../store/useLoadingStore";
import type { RegisterFormInputs } from "../../utils/interfaces";

const Register = () => {
  const navigate = useNavigate();
  const setUserId = useAuthStore((state) => state.setUserId);
  const { isLoading, setIsLoading } = useLoadingStore((state) => state);
  const [showPass, setShowPass] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormInputs>({
    resolver: zodResolver(registerSchema),
    mode: "onChange",
  });

  const onSubmit: SubmitHandler<RegisterFormInputs> = async (
    data: RegisterFormInputs,
  ) => {
    try {
      setIsLoading(true);
      const userId = await registerUser(data);
      setUserId(userId);
      navigate("/dashboard");
    } catch (err: unknown) {
      setIsLoading(false);

      if (axios.isAxiosError(err)) {
        const status = err.response?.status;

        if (status === 400) {
          const errorMsg =
            err.response?.data?.detail ??
            "Failed to register, please try again";
          toast.error(errorMsg);
        } else {
          toast.error("An error occurred during registration");
        }
      } else {
        toast.error("Failed to connect to the server");
      }
    }
  };

  return (
    <div className="login-register-container">
      <form id="register-form" onSubmit={handleSubmit(onSubmit)}>
        <h1 className="login-register-title">Register</h1>
        <div className="login-register-inputbox">
          <input
            id="username"
            type="text"
            required
            autoComplete="off"
            {...register("username")}
          />
          <label htmlFor="username">Username</label>
          {errors.username && (
            <span className="login-register-error-message">
              {errors.username.message}
            </span>
          )}
        </div>
        <div className="login-register-inputbox">
          <input
            id="password"
            type={!showPass ? "password" : "text"}
            required
            {...register("password")}
          />
          <label htmlFor="password">Password</label>
          {!showPass ? (
            <IoEye className="eye-icon" onClick={() => setShowPass(true)} />
          ) : (
            <IoEyeOff className="eye-icon" onClick={() => setShowPass(false)} />
          )}
          {errors.password && (
            <span className="login-register-error-message">
              {errors.password.message}
            </span>
          )}
        </div>
        <div className="login-register-inputbox">
          <input
            id="email"
            type="text"
            required
            autoComplete="off"
            {...register("email")}
          />
          <label htmlFor="email">Email</label>
          {errors.email && (
            <span className="login-register-error-message">
              {errors.email.message}
            </span>
          )}
        </div>
        <button
          type="submit"
          className="login-register-btn"
          disabled={isLoading}
        >
          Register
        </button>
        <div className="login-register-link">
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Register;
