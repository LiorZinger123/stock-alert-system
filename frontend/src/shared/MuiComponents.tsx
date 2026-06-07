import React from 'react';
import { Controller } from 'react-hook-form';
import type { Control, FieldValues, RegisterOptions, Path } from "react-hook-form"
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';

interface CustomTextFieldProps<TFieldValues extends FieldValues> {
  name: Path<TFieldValues>;
  control: Control<TFieldValues>; 
  label: string;
  type?: string;
  rules?: RegisterOptions;
  icon?: React.ReactNode;
}

export const CustomTextField = <TFieldValues extends FieldValues>({ 
  name, 
  control, 
  label, 
  type = "text", 
  rules, 
  icon,
  ...props 
}: CustomTextFieldProps<TFieldValues>) => {
  return (
    <Controller
      name={name}
      control={control as any} 
      rules={rules}
     render={({ field, fieldState: { error } }) => (
      <TextField
  {...field}
  label={label}
  type={type}
  error={!!error}
  helperText={error ? error.message : null}
  fullWidth
  margin="normal"
  variant="outlined"
  {...props}
  slotProps={{
    input: {
      startAdornment: icon ? (
        <InputAdornment position="start" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {icon}
        </InputAdornment>
      ) : undefined,
    },
  }}
  sx={{
    '& .MuiInputLabel-root': { 
      color: 'white',
      transform: 'translate(42px, 16px) scale(1)', // מיקום התחלתי — מזיז ימינה לפי רוחב האייקון
    },
    '& .MuiInputLabel-root.MuiInputLabel-shrink': {
      transform: 'translate(14px, -9px) scale(0.75)', // מיקום כשעולה למעלה — חוזר למקום רגיל
    },
    '& .MuiInputLabel-root.Mui-focused': { color: 'white' },
    '& .MuiInputBase-input': { color: 'white' },
    '& .MuiOutlinedInput-root': {
      '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.23)' },
      '&:hover fieldset': { borderColor: 'white' },
      '&.Mui-focused fieldset': { borderColor: 'white' },
    },
    '& .MuiInputBase-input:-webkit-autofill': {
      WebkitBoxShadow: '0 0 0 100px #1E1E1E inset !important',
      WebkitTextFillColor: 'white !important',
      transition: 'background-color 9999s ease-in-out 0s',
    },
    '& .MuiOutlinedInput-root:-webkit-autofill': {
      borderColor: 'white !important',
    }
  }}
/>
      )}
    />
  );
};