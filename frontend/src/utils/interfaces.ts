export interface LoginFormInputs {
  username: string;
  password: string;
}

export interface RegisterFormInputs extends LoginFormInputs {
  email: string
}