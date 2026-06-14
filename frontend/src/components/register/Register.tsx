import { useState, useEffect, Activity } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import { useForm, type SubmitHandler } from "react-hook-form";
import Loader from "../Loader/Loader";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerUser } from "../../services/api/authService";
import type { RegisterFormInputs } from "../../utils/interfaces";
import { registerSchema } from "../../utils/schemas";


const Register = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState<boolean>(false);
    const [showErrors, setShowErrors] = useState<Record<string, boolean>>({});
    const {
        register,
        handleSubmit,
        formState: { errors }
    } = useForm<RegisterFormInputs>({
        resolver: zodResolver(registerSchema),
        mode: "onChange",
    });

    const onSubmit: SubmitHandler<RegisterFormInputs> = async(data: RegisterFormInputs) => {
        try {
            setLoading(true);
            await registerUser(data)

            navigate("/dashboard")
        } catch (err: any) {
            const status = err.response?.status;

            if (status === 400) {
                const errorMsg = err.response?.data?.detail ?? "Failed to register, please try again"
                toast.error(errorMsg);
            } else {
                toast.error("Failed to login, please try again");
            }
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setShowErrors({ 
                username: !!errors.username, 
                password: !!errors.password, 
                email: !!errors.email 
            });

            const timer = setTimeout(() => {
                setShowErrors({});
            }, 3000);

            return () => clearTimeout(timer);
        }
    }, [errors]);

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
                    {errors.username && showErrors.username && (
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
                    {errors.password && showErrors.password && (
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
                    {errors.email && showErrors.email && (
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
  )
}

export default Register