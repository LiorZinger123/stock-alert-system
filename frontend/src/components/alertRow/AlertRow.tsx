import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FiEdit2 } from "react-icons/fi";
import { MdDeleteOutline } from "react-icons/md";
import type { Alert } from "../../utils/interfaces"
import UpdateAlertForm from "../updateAlertForm/UpdateAlertForm";
import { CustomDialog, GlassModal } from "../../shared/MuiComponents";
import { useDeleteAlert } from "../../services/queries/alertQueries";
import './alertRow.scss'

interface AlertRowProps {
    alert: Alert;
    setIsPendingUpdate: (value: boolean) => void;
    setIsPendingDelete: (value: boolean) => void;
}

const AlertRow = ({ alert, setIsPendingUpdate, setIsPendingDelete }: AlertRowProps) => {
  const [alertId, setAlertId] = useState<number>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openUpdateDialog, setOpenUpdateDialog] = useState(false);
  const { mutate: deleteAlert, isPending: isPendingDelete } = useDeleteAlert();

  const openUpdateAlertDialog = (alertId: number) => {
    setOpenUpdateDialog(true);
    setAlertId(alertId);
  };

  const onCloseUpdateDialog = () => {
    setOpenUpdateDialog(false)
    setAlertId(undefined);
  };

  const openDeleteAlertDialog = (alertId: number) => {
    setOpenDeleteDialog(true);
    setAlertId(alertId);
  };

  const onCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
    setAlertId(undefined);
  };

    const handleDelete = () => {
    if (alertId) {
      deleteAlert(alertId, {
        onSuccess: () => {
          onCloseDeleteDialog()
          toast.success("Alert deleted successfully");
        },
        onError: () => {
          toast.error("Deletion Failed, Please Try Again Later");
        }
      });
    } else {
      toast.error("Deletion Failed, Please Try Again Later");
    }
  };

  useEffect(() => {
    setIsPendingDelete(isPendingDelete);
  }, [isPendingDelete])  

  return (
    <>
      <div className="alert-row">
        <div className="alert-symbol">
          <span className="symbol">{alert.asset.symbol.toUpperCase()}</span>
          <span className="name">{alert.asset.name}</span>
        </div>
        <div className="alert-trigger">
          <span>Trigger {alert.condition === 'above' ? '>' : '<'}=</span>
          <span className="price-value">${alert.target_price}</span>
        </div>
        <div className="alert-status">
          {alert.status.toUpperCase()}
        </div>
        <div className="alert-row-actions">
          <FiEdit2 className="alert-row-action edit-icon" onClick={() => openUpdateAlertDialog(alert.id)} />
          <MdDeleteOutline className="alert-row-action delete-icon" onClick={() => openDeleteAlertDialog(alert.id)} />
        </div>
      </div>
      <CustomDialog 
        open={openDeleteDialog}
        onClose={onCloseDeleteDialog}
        title="Do you want to delete this alert?"
        description="This change is permanent."
        onClick={handleDelete}
      />
      <GlassModal open={openUpdateDialog} onClose={onCloseUpdateDialog}>
        <UpdateAlertForm alert={alert} onClose={onCloseUpdateDialog} setLoading={setIsPendingUpdate} />
      </GlassModal>
    </>
  )
}

export default AlertRow