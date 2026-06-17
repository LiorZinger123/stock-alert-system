import { useState, Activity } from "react";
import { useNavigate, Link } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, type SubmitHandler } from "react-hook-form";
import axios from "axios";
import toast from "react-hot-toast";
import Loader from "../Loader/Loader";
import { registerSchema } from "../../utils/schemas";
import { registerUser } from "../../services/api/authService";
import type { RegisterFormInputs } from "../../utils/interfaces";

const Register = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState<boolean>(false);
    
    const {
        register,
        handleSubmit,
        formState: { errors, touchedFields }
    } = useForm<RegisterFormInputs>({
        resolver: zodResolver(registerSchema),
        mode: "onBlur",
    });

    const onSubmit: SubmitHandler<RegisterFormInputs> = async (data: RegisterFormInputs) => {
        try {
            setLoading(true);
            await registerUser(data);
            navigate("/dashboard");
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                const status = err.response?.status;
                
                if (status === 400) {
                    const errorMsg = err.response?.data?.detail ?? "Failed to register, please try again";
                    toast.error(errorMsg);
                } else {
                    toast.error("An error occurred during registration");
                }
            } else {
                toast.error("Failed to connect to the server");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="login-register-container">
                <form id='register-form' onSubmit={handleSubmit(onSubmit)}>
                    <h1 className='login-register-title'>Register</h1>
                    <div className="login-register-inputbox">
                        <input 
                            id='username' 
                            type="text" 
                            required
                            autoComplete='off'
                            {...register("username")} 
                        />
                        <label htmlFor="username">Username</label>
                        {touchedFields.username && errors.username && (
                            <span className="login-register-error-message">{errors.username.message}</span>
                        )}
                    </div>
                    <div className="login-register-inputbox">
                        <input 
                            id="password" 
                            type="password" 
                            required
                            {...register("password")} 
                        />
                        <label htmlFor='password'>Password</label>
                        {touchedFields.password && errors.password && (
                            <span className="login-register-error-message">{errors.password.message}</span>
                        )}
                    </div>
                    <div className="login-register-inputbox">
                        <input 
                            id="email" 
                            type="text" 
                            required
                            autoComplete='off'
                            {...register("email")} 
                        />
                        <label htmlFor='email'>Email</label>
                        {touchedFields.email && errors.email && (
                            <span className="login-register-error-message">{errors.email.message}</span>
                        )}
                    </div>
                    <button type="submit" className='login-register-btn' disabled={loading}>
                        Register
                    </button>
                    <div className="login-register-link">
                        <p>Already have an account? <Link to="/login">Login</Link></p>
                    </div>
                </form>
            </div>
            <Activity mode={loading ? 'visible' : 'hidden'}>
                <Loader />
            </Activity>
        </>
    );
};

export default Register;