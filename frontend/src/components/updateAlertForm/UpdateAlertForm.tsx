import { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { useUpdateAlert } from '../../services/queries/alertQueries';
import { DialogTitle, DialogContent, DialogActions } from '@mui/material';
import type { Alert, UpdateAlertFormValues } from '../../utils/interfaces';
import { conditionOptions, updateAlertStatusOptions } from '../../utils/constants';
import {
  ActionButton,
  CustomSelect,
  CustomTextField,
} from '../../shared/MuiComponents';

interface UpdateAlertFormProps {
  alert: Alert;
  onClose: () => void;
  setLoading: (value: boolean) => void;
}

const UpdateAlertForm = ({ alert, onClose, setLoading }: UpdateAlertFormProps) => {
  const { control, handleSubmit } = useForm<UpdateAlertFormValues>({
    defaultValues: {
      targetPrice: String(alert.target_price),
      condition: alert.condition,
      status: alert.status,
    },
  });

  const { mutate, isPending } = useUpdateAlert();

  const onSubmit = (data: UpdateAlertFormValues) => {
    const target_price = Number(data.targetPrice);

    if (!Number.isFinite(target_price) || target_price <= 0) {
      toast.error('Target price must be a valid number greater than 0');
      return;
    }

    mutate(
      {
        alertId: alert.id,
        data: {
          target_price,
          condition: data.condition,
          status: data.status,
        },
      },
      {
        onSuccess: () => {
          toast.success('Alert updated successfully');
          onClose();
        },
        onError: () => {
          toast.error('Failed to update alert');
        },
      }
    );
  };

  useEffect(() => {
    setLoading(isPending);
  }, [isPending, setLoading]);

  return (
    <>
      <DialogTitle className="new-update-alert-form-title">Update Alert</DialogTitle>
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
          <ActionButton onClick={onClose} variant="outlined" color="inherit" className="new-update-alert-cancel-button">
            Cancel
          </ActionButton>
          <ActionButton type="submit" variant="contained" color="error" disableElevation>
            Update
          </ActionButton>
        </DialogActions>
      </form>
    </>
  );
};

export default UpdateAlertForm;
