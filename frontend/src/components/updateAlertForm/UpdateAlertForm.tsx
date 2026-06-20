import { useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import { Controller, useForm } from "react-hook-form";
import { isDuplicateAlert } from "../../utils/helpers";
import { useLoadingStore } from "../../store/useLoadingStore";
import { DialogTitle, DialogContent, DialogActions } from "@mui/material";
import type { Alert, UpdateAlertFormValues } from "../../utils/interfaces";
import {
  conditionOptions,
  updateAlertStatusOptions,
} from "../../utils/constants";
import {
  ActionButton,
  CustomSelect,
  CustomTextField,
} from "../../shared/MuiComponents";
import {
  useUpdateAlert,
  useInfiniteAlerts,
} from "../../services/queries/alertQueries";

interface UpdateAlertFormProps {
  alert: Alert;
  onClose: () => void;
}

const UpdateAlertForm = ({ alert, onClose }: UpdateAlertFormProps) => {
  const { setIsLoading } = useLoadingStore();
  const { data: alerts } = useInfiniteAlerts();

  const { control, handleSubmit } = useForm<UpdateAlertFormValues>({
    defaultValues: {
      targetPrice: String(alert.target_price),
      condition: alert.condition,
      status: alert.status,
    },
  });

  const { mutate, isPending } = useUpdateAlert();

  const onSubmit = (data: UpdateAlertFormValues): void => {
    const target_price = Number(data.targetPrice);
    const allAlerts = alerts?.pages.flatMap((page) => page) || [];

    if (!Number.isFinite(target_price) || target_price <= 0) {
      toast.error("Target price must be a valid number greater than 0");
      return;
    }

    if (
      isDuplicateAlert(
        allAlerts,
        alert.asset.symbol,
        target_price,
        data.condition,
        alert.id,
      )
    ) {
      toast.error("You already have an identical alert for this asset.");
      return;
    }

    mutate(
      {
        alertId: alert.id,
        data: {
          symbol: alert.asset.symbol,
          target_price,
          condition: data.condition,
          status: data.status,
        },
      },
      {
        onSuccess: () => {
          toast.success("Alert updated successfully");
          onClose();
        },
        onError: (error) => {
          if (axios.isAxiosError(error) && error.response?.status === 409) {
            toast.error("An identical alert already exists.");
          } else {
            toast.error("Failed to update alert");
          }
        },
      },
    );
  };

  useEffect(() => {
    setIsLoading(isPending);
  }, [isPending, setIsLoading]);

  return (
    <>
      <DialogTitle className="new-update-alert-form-title">
        Update Alert
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent className="new-update-alert-form-content">
          <CustomTextField
            label="Stock"
            value={alert.asset.name}
            disabled
            fullWidth
          />
          <Controller
            name="targetPrice"
            control={control}
            render={({ field }) => (
              <CustomTextField
                {...field}
                label="Target Price"
                type="number"
                fullWidth
              />
            )}
          />
          <Controller
            name="condition"
            control={control}
            render={({ field }) => (
              <CustomSelect
                label="Condition"
                value={field.value}
                onChange={field.onChange}
                options={conditionOptions}
              />
            )}
          />
          <Controller
            name="status"
            control={control}
            render={({ field }) => (
              <CustomSelect
                label="Status"
                value={field.value}
                onChange={field.onChange}
                options={updateAlertStatusOptions}
              />
            )}
          />
        </DialogContent>
        <DialogActions className="new-update-alert-form-dialog-actions">
          <ActionButton
            onClick={onClose}
            variant="outlined"
            color="inherit"
            className="new-update-alert-cancel-button"
          >
            Cancel
          </ActionButton>
          <ActionButton
            type="submit"
            variant="contained"
            color="error"
            disableElevation
          >
            Update
          </ActionButton>
        </DialogActions>
      </form>
    </>
  );
};

export default UpdateAlertForm;
