import { useState, Activity, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm, type SubmitHandler } from "react-hook-form";
import toast from 'react-hot-toast';
import Loader from '../Loader/Loader';
import api from '../../services/api/api';
import { login } from "../../services/api/authService";
import type { LoginFormInputs } from "../../utils/interfaces";

const Login = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState<boolean>(false);
    const { register, handleSubmit } = useForm<LoginFormInputs>();

    const onSubmit: SubmitHandler<LoginFormInputs> = async(data: LoginFormInputs) => {
        try {
            setLoading(true);
            await login(data);
            
            navigate("/dashboard");
       } catch (err: any) {
            const status = err.response?.status;

            if (status === 400) {
                toast.error("Username or password is incorrect");
            } else {
                toast.error("Failed to login, please try again");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const checkAuth = async () => {
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
    }, []);

    return (
        <>
            <div className='login-register-container'>
                <form id='login-form' onSubmit={handleSubmit(onSubmit)}>
                    <h1 className='login-register-title'>Login</h1>
                    <div className="login-register-inputbox">
                        <input 
                            id='username' 
                            type="text" 
                            required
                            autoComplete='off'
                            {...register("username", { required: true })} 
                        />
                        <label htmlFor="username">Username</label>
                    </div>
                    <div className="login-register-inputbox">
                        <input 
                            id="password" 
                            type="password" 
                            required
                            {...register("password", { required: true })} 
                        />
                        <label htmlFor='password'>Password</label>
                    </div>
                    <button type="submit" className='login-register-btn' disabled={loading}>
                        Log in
                    </button>
                    <div className="login-register-link">
                        <p>Don't have an account? <Link to="/register">Register</Link></p>
                    </div>
                </form>
            </div>
            <Activity mode={loading ? 'visible' : 'hidden'}>
                <Loader />
            </Activity>
        </>
    )
}

export default Login;