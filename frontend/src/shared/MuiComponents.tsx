import React from "react";
import {
  Slide,
  Dialog,
  Button,
  Select,
  MenuItem,
  TextField,
  InputLabel,
  FormControl,
  DialogTitle,
  Autocomplete,
  DialogContent,
  DialogActions,
  DialogContentText,
  type PaperProps,
  type ButtonProps,
  type TextFieldProps,
  type SelectChangeEvent,
  type AutocompleteProps,
} from "@mui/material";
import type { TransitionProps } from "@mui/material/transitions";

interface CustomTextFieldProps extends Omit<TextFieldProps, "variant"> {
  label: string;
}

export const CustomTextField = ({
  label,
  value,
  onChange,
  fullWidth = true,
  type,
  sx,
  ...rest
}: CustomTextFieldProps) => {
  return (
    <TextField
      {...rest}
      label={label}
      value={value}
      onChange={onChange}
      fullWidth={fullWidth}
      variant="outlined"
      autoComplete="off"
      type={type}
      sx={{
        "& .MuiInputLabel-root": {
          color: "white",
        },
        "& .MuiInputLabel-root.Mui-focused": {
          color: "white",
        },
        "& .MuiInputLabel-root.MuiInputLabel-shrink": {
          color: "white",
        },
        "& .MuiInputBase-input:-webkit-autofill": {
          WebkitBoxShadow:
            "0 0 0 100px rgba(255, 255, 255, 0.1) inset !important",
          WebkitTextFillColor: "white !important",
          borderRadius: "8px",
        },
        "& .MuiOutlinedInput-root": {
          color: "white",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(255, 255, 255, 0.5)",
            transition: "0.2s",
          },

          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "white",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "white",
            borderWidth: "2px",
          },
        },
        "& input::-webkit-outer-spin-button, & input::-webkit-inner-spin-button":
          {
            WebkitAppearance: "none",
            margin: 0,
          },

        "& input[type=number]": {
          MozAppearance: "textfield",
        },
        "& .Mui-disabled": {
          color: "rgba(255, 255, 255, 0.3) !important",
          WebkitTextFillColor: "rgba(255, 255, 255, 0.3) !important",

          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(255, 255, 255, 0.15) !important",
          },
        },
        "& .MuiInputLabel-root.Mui-disabled": {
          color: "rgba(255, 255, 255, 0.3) !important",
        },
        ...sx,
      }}
    />
  );
};

interface CustomSelectProps {
  label: string;
  value: string;
  options: { label: string; value: string }[];
  onChange: (event: SelectChangeEvent<string>) => void;
}

export const CustomSelect = ({
  label,
  value,
  onChange,
  options,
}: CustomSelectProps) => {
  return (
    <FormControl fullWidth>
      <InputLabel sx={{ color: "white !important" }}>{label}</InputLabel>
      <Select
        value={value}
        onChange={onChange}
        label={label}
        MenuProps={{
          slotProps: {
            paper: {
              sx: {
                background: "rgba(255, 255, 255, 0.1)",
                backdropFilter: "blur(10px)",
                color: "white",
                border: "1px solid rgba(255, 255, 255, 0.2)",
              },
            },
          },
        }}
        sx={{
          color: "white",
          ".MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(255, 255, 255, 0.5)",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "white" },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "white",
          },
          ".MuiSvgIcon-root": { color: "white" },
        }}
      >
        {options.map((opt) => (
          <MenuItem
            key={opt.value}
            value={opt.value}
            sx={{ "&:hover": { background: "rgba(255, 255, 255, 0.15)" } }}
          >
            {opt.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

interface GlassModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export const GlassModal = ({ open, onClose, children }: GlassModalProps) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      slots={{ transition: Transition }}
      fullWidth
      maxWidth="xs"
      sx={{
        "& .MuiDialog-paper": {
          background: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(20px)",
          borderRadius: "20px",
          color: "white",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          willChange: "backdrop-filter",
          outline: "None",
        },
      }}
    >
      {children}
    </Dialog>
  );
};

export const ActionButton = ({ children, sx, ...props }: ButtonProps) => {
  return (
    <Button
      {...props}
      sx={{
        textTransform: "none",
        borderRadius: "12px",
        px: 3,
        ...sx,
      }}
    >
      {children}
    </Button>
  );
};

export const CustomAutocomplete = <T,>(
  props: AutocompleteProps<T, false, false, false>,
) => {
  return (
    <Autocomplete
      {...props}
      sx={{
        "& .MuiAutocomplete-endAdornment .MuiSvgIcon-root": { color: "white" },
        ...props.sx,
      }}
      slotProps={{
        ...props.slotProps,
        paper: {
          ...(props.slotProps?.paper as PaperProps),
          sx: {
            background: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(10px)",
            color: "white",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            "& .MuiAutocomplete-option:hover": {
              background: "rgba(255, 255, 255, 0.15)",
            },
            "& .MuiAutocomplete-noOptions": {
              color: "white",
            },
            "& .MuiAutocomplete-loading": {
              color: "white",
            },
            ...(props.slotProps?.paper as PaperProps)?.sx,
          },
        },
      }}
    />
  );
};

interface CustomDialogProps {
  open: boolean;
  title: string;
  description: string;
  onClose: () => void;
  onClick: () => void;
}

const Transition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

export const CustomDialog = ({
  open,
  onClose,
  title,
  description,
  onClick,
}: CustomDialogProps) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      slots={{ transition: Transition }}
      sx={{
        "& .MuiDialog-paper": {
          width: "450px",
          borderRadius: "20px",
          padding: "8px",
          background: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          boxShadow: "0px 10px 30px rgba(0,0,0,0.3)",
          color: "white",
          outline: "none",
        },
      }}
    >
      <DialogTitle sx={{ fontWeight: "700", pb: 1, color: "white" }}>
        {title}
      </DialogTitle>
      <DialogContent>
        <DialogContentText
          sx={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "0.95rem" }}
        >
          {description}
        </DialogContentText>
      </DialogContent>
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <ActionButton
          onClick={onClose}
          variant="outlined"
          color="inherit"
          sx={{
            borderColor: "rgba(255, 255, 255, 0.3)",
          }}
        >
          Cancel
        </ActionButton>
        <ActionButton
          onClick={onClick}
          variant="contained"
          color="error"
          disableElevation
        >
          confirm
        </ActionButton>
      </DialogActions>
    </Dialog>
  );
};
