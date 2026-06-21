import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import UpdateAlertForm from "../updateAlertForm/UpdateAlertForm";
import { Tooltip } from "@mui/material";
import { FiEdit2 } from "react-icons/fi";
import { MdDeleteOutline } from "react-icons/md";
import type { Alert } from "../../utils/interfaces";
import { alertStatusMap } from "../../utils/constants";
import { useLoadingStore } from "../../store/useLoadingStore";
import { useDeleteAlert } from "../../services/queries/alertQueries";
import { CustomDialog, GlassModal } from "../../shared/MuiComponents";
import "./alertRow.scss";

interface AlertRowProps {
  alert: Alert;
}

const AlertRow = ({ alert }: AlertRowProps) => {
  const { setIsLoading } = useLoadingStore();
  const [openDeleteDialog, setOpenDeleteDialog] = useState<boolean>(false);
  const [openUpdateDialog, setOpenUpdateDialog] = useState<boolean>(false);
  const [isFlashing, setIsFlashing] = useState(false);

  useEffect(() => {
    setIsFlashing(true);
    const timer = setTimeout(() => setIsFlashing(false), 1500);
    return () => clearTimeout(timer);
  }, [alert.triggered_price, alert.status]);

  const disabledStatuses = [
    alertStatusMap.pending,
    alertStatusMap.sent,
    alertStatusMap.failed,
  ];
  const isDeleteDisabled = disabledStatuses.includes(alert.status);

  const { mutate: deleteAlert, isPending: isPendingDelete } = useDeleteAlert();

  const handleDelete = (): void => {
    if (disabledStatuses.includes(alert.status)) {
      toast.error("This alert cannot be deleted in its current state.");
      return;
    }

    deleteAlert(alert.id, {
      onSuccess: () => {
        setOpenDeleteDialog(false);
        toast.success("Alert deleted successfully");
      },
      onError: (error) => {
        if (axios.isAxiosError(error) && error.response) {
          const status = error.response.status;
          if (status === 409) {
            toast.error("This alert cannot be deleted in its current state.");
          } else if (status === 423) {
            toast.error("Alert is currently being processed, please wait.");
          } else {
            toast.error("Deletion Failed, Please Try Again Later");
          }
        } else {
          toast.error("Deletion Failed, Please Try Again Later");
        }
      },
    });
  };

  useEffect(() => {
    setIsLoading(isPendingDelete);
  }, [isPendingDelete, setIsLoading]);

  return (
    <>
      <div className={`alert-row ${isFlashing ? "flash-effect" : ""}`}>
        <Tooltip
          title={`${alert.asset.symbol.toUpperCase()} - ${alert.asset.name}`}
          arrow
        >
          <div className="alert-symbol-name">
            <span className="symbol">{alert.asset.symbol.toUpperCase()}</span>
            <span className="name">{alert.asset.name}</span>
          </div>
        </Tooltip>
        <div className="alert-trigger">
          <span className="label">Trigger</span>
          <span className="price-value">{alert.condition === "above" ? ">" : "<"}= {alert.target_price}$</span>
        </div>
        {alert.status !== alertStatusMap.inactive &&
          <div className="alert-current-triggered-price">
            <span className="label">{!!alert.triggered_price ? "Triggered" : "Current"} Price</span>
            <span className={`price-value ${isFlashing ? "flash-effect" : ""}`}>
              {alert.triggered_price ?? alert.asset.price}$
            </span>
          </div>  
        }
        <div className={`alert-status ${alert.status} ${isFlashing ? "flash-effect" : ""}`}>
          {alert.status.toUpperCase()}
        </div>
        <div className="alert-row-actions">
          <FiEdit2
            className="alert-row-action edit-icon"
            onClick={() => setOpenUpdateDialog(true)}
          />
          <Tooltip
            title={
              isDeleteDisabled ? `Cannot delete ${alert.status} alerts` : ""
            }
            arrow
          >
            <span>
              <MdDeleteOutline
                className={`alert-row-action delete-icon${isDeleteDisabled ? " disabled" : ""}`}
                onClick={() => !isDeleteDisabled && setOpenDeleteDialog(true)}
              />
            </span>
          </Tooltip>
        </div>
      </div>
      <CustomDialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
        title="Do you want to delete this alert?"
        description="This change is permanent."
        onClick={handleDelete}
      />
      <GlassModal
        open={openUpdateDialog}
        onClose={() => setOpenUpdateDialog(false)}
      >
        <UpdateAlertForm
          alert={alert}
          onClose={() => setOpenUpdateDialog(false)}
        />
      </GlassModal>
    </>
  );
};

export default AlertRow;