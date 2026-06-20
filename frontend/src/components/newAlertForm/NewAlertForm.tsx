import { useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import { Controller, useForm } from "react-hook-form";
import { DialogTitle, DialogContent, DialogActions } from "@mui/material";
import AssetSearchBar from "../assetSearchBar/AssetSearchBar";
import { isDuplicateAlert } from "../../utils/helpers";
import { conditionOptions } from "../../utils/constants";
import { useLoadingStore } from "../../store/useLoadingStore";
import type {
  AlertCondition,
  NewAlertFormValues,
} from "../../utils/interfaces";
import {
  useCreateAlert,
  useInfiniteAlerts,
} from "../../services/queries/alertQueries";
import {
  ActionButton,
  CustomSelect,
  CustomTextField,
} from "../../shared/MuiComponents";

interface NewAlertFormProps {
  onClose: () => void;
}

const NewAlertForm = ({ onClose }: NewAlertFormProps) => {
  const { setIsLoading } = useLoadingStore();
  const { data: alerts } = useInfiniteAlerts();

  const { control, handleSubmit } = useForm<NewAlertFormValues>({
    defaultValues: {
      asset: null,
      targetPrice: "",
      condition: "" as AlertCondition,
    },
  });

  const { mutate, isPending } = useCreateAlert();

  useEffect(() => {
    setIsLoading(isPending);
  }, [isPending, setIsLoading]);

  const onSubmit = (data: NewAlertFormValues) => {
    if (!data.asset) {
      toast.error("Alert Creation Failed: Asset is required.");
      return;
    }

    const allAlerts = alerts?.pages.flatMap((page) => page) || [];
    const targetPrice = Number(data.targetPrice);

    if (
      isDuplicateAlert(
        allAlerts,
        data.asset.symbol,
        targetPrice,
        data.condition,
      )
    ) {
      toast.error("You already have an identical alert for this asset.");
      return;
    }

    mutate(
      {
        symbol: data.asset.symbol,
        name: data.asset.name,
        target_price: targetPrice,
        condition: data.condition as AlertCondition,
      },
      {
        onSuccess: () => {
          onClose();
          toast.success("Alert Created Successfully!");
        },
        onError: (error) => {
          if (axios.isAxiosError(error) && error.response?.status === 409) {
            toast.error("You already have an identical alert for this asset.");
          } else {
            toast.error("Failed to create alert. Please try again later.");
          }
        },
      },
    );
  };

  return (
    <>
      <DialogTitle className="new-update-alert-form-title">
        Add New Alert
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent className="new-update-alert-form-content">
          <Controller
            name="asset"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <AssetSearchBar
                key={field.value ? field.value.symbol : "reset"}
                field={field}
              />
            )}
          />
          <Controller
            name="targetPrice"
            control={control}
            rules={{
              required: "Target price is required",
              validate: (v) =>
                Number.isInteger(Number(v)) || "Value must be a valid integer",
            }}
            render={({ field, fieldState }) => (
              <CustomTextField
                {...field}
                label="Target Price"
                type="number"
                error={!!fieldState.error}
                helperText={fieldState.error?.message}
              />
            )}
          />
          <Controller
            name="condition"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <CustomSelect
                label="Alert Condition"
                value={field.value}
                onChange={field.onChange}
                options={conditionOptions}
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
            Confirm
          </ActionButton>
        </DialogActions>
      </form>
    </>
  );
};

export default NewAlertForm;
