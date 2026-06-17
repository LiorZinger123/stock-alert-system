import { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { conditionOptions } from '../../utils/constants';
import AssetSearchBar from '../assetSearchBar/AssetSearchBar';
import { useCreateAlert } from '../../services/queries/alertQueries';
import type { AlertCondition, NewAlertFormValues } from '../../utils/interfaces';
import { ActionButton, CustomSelect, CustomTextField } from '../../shared/MuiComponents';

interface NewAlertFormProps {
  onClose: () => void;
  setLoading: (value: boolean) => void;
}

const NewAlertForm = ({ onClose, setLoading }: NewAlertFormProps) => {
  const { control, handleSubmit } = useForm<NewAlertFormValues>({
    defaultValues: {
      asset: null,
      targetPrice: '',
      condition: '' as AlertCondition,
    }
  });
  const { mutate, isPending } = useCreateAlert();

  const onSubmit = (data: NewAlertFormValues) => {
    if (!data.asset) {
      return;
    }

    const finalTargetPrice = Number(data.targetPrice);

    if (Number.isNaN(finalTargetPrice) || !Number.isInteger(finalTargetPrice)) {
      return "Value must be a valid integer";
    }

    const finalData = {
      symbol: data.asset.symbol,
      target_price: finalTargetPrice,
      condition: data.condition as AlertCondition,
    }

    mutate(finalData, {
      onSuccess: () => {
        onClose();
        toast.success("Alert Created Successfully!")
      },
      onError: () => {
        toast.error("Alert Created Failed, Please Try Again Later.")
      }
    })
  };

  useEffect(() => {
    setLoading(isPending);
  }, [isPending, setLoading])

  return (
    <>
      <DialogTitle className="new-update-alert-form-title">Add New Alert</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent className="new-update-alert-form-content">
          <Controller
            name="asset"
            control={control}
            render={({ field }) => (
              <AssetSearchBar field={field} />
            )}
          />
          <Controller
            name="targetPrice"
            control={control}
            render={({ field }) => (
              <CustomTextField {...field} label="Target Price" type="number" />
            )}
          />
          <Controller
            name="condition"
            control={control}
            render={({ field }) => (
              <CustomSelect label="Alert Condition" value={field.value} onChange={field.onChange} options={conditionOptions} />
            )}
          />
        </DialogContent>
        <DialogActions className="new-update-alert-form-dialog-actions">
          <ActionButton onClick={onClose} variant="outlined" color="inherit" className="new-update-alert-cancel-button">
            Cancel
          </ActionButton>
          <ActionButton type="submit" variant="contained" color="error" disableElevation>
            Confirm
          </ActionButton>
        </DialogActions>
      </form>
    </>
  );
};

export default NewAlertForm;
