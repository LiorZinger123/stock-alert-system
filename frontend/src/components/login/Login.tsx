import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm, type SubmitHandler } from "react-hook-form";
import axios from 'axios';
import toast from 'react-hot-toast';
import api from '../../services/api/api';
import { IoEye } from "react-icons/io5";
import { IoEyeOff } from "react-icons/io5";
import { login } from "../../services/api/authService";
import type { LoginFormInputs } from "../../utils/interfaces";
import { useLoadingStore } from '../../store/useLoadingStore';

const Login = () => {
    const navigate = useNavigate();
    const { isLoading, setIsLoading } = useLoadingStore((state) => state);
    const { register, handleSubmit } = useForm<LoginFormInputs>();
    const [showPass, setShowPass] = useState(false);

   const onSubmit: SubmitHandler<LoginFormInputs> = async (data: LoginFormInputs) => {
        try {
            setIsLoading(true);
            await login(data);
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
            localStorage.removeItem('auth_manual_logout');
        }
    };

    useEffect(() => {
        const checkAuth = async () => {
            const isManuallyLoggedOut = localStorage.getItem('auth_manual_logout') === 'true';

            if (isManuallyLoggedOut) {
                console.log("User manually logged out; skipping auto-login.");
                return;
            }

            try {
                await api.get("/me", { 
                    withCredentials: true,
                    skipAuthInterceptor: true 
                });

                navigate("/dashboard");
            } catch {
                console.log("User not logged in");
            }
        };

        checkAuth();
    }, [navigate]);

    return (
        <div className='login-register-container'>
            <form id='login-form' onSubmit={handleSubmit(onSubmit)}>
                <h1 className='login-register-title'>Login</h1>
                <div className="login-register-inputbox">
                    <input 
                        id='username'
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
                    <label htmlFor='password'>Password</label>
                    {!showPass ? (
                        <IoEye className="eye-icon" onClick={() => setShowPass(true)} />
                    ) : (
                        <IoEyeOff className="eye-icon" onClick={() => setShowPass(false)} />
                    )}
                </div>
                <button type="submit" className='login-register-btn' disabled={isLoading}>
                    Log in
                </button>
                <div className="login-register-link">
                    <p>Don't have an account? <Link to="/register">Register</Link></p>
                </div>
            </form>
        </div>
    )
}

export default Login;