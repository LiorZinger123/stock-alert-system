import { Activity, useState } from "react";
import Loader from "../Loader/Loader";
import AlertRow from "../alertRow/AlertRow";
import NewAlertForm from "../newAlertForm/NewAlertForm";
import { GlassModal } from "../../shared/MuiComponents";
import { useGetAlerts } from "../../services/queries/alertQueries";
import './alertsList.scss'

const AlertsList = () => {
  const { data: alerts, isLoading, error } = useGetAlerts();
  const [createLoading, setCreateLoading] = useState(false);
  const [openNewAlertDialog, setOpenNewAlertDialog] = useState(false);
  const [isPendingUpdate, setIsPendingUpdate] = useState(false);
  const [isPendingDelete, setIsPendingDelete] = useState(false);
  const globalLoading = isPendingUpdate || isPendingDelete || createLoading;

  return (
    <>
      <div className="alerts-list-wrapper">
        <div className="alerts-list">
          {alerts?.length ? (
            alerts.map((alert) => <AlertRow key={alert.id} alert={alert} setIsPendingUpdate={setIsPendingUpdate} setIsPendingDelete={setIsPendingDelete} />)
          ) : (
            <p>No alerts found.</p>
          )}
        </div>
        <button className="add-alert-btn" onClick={() => setOpenNewAlertDialog(true)}>ADD NEW ALERT</button>
      </div> 
      <GlassModal open={openNewAlertDialog} onClose={() => setOpenNewAlertDialog(false)}>
        <NewAlertForm onClose={() => setOpenNewAlertDialog(false)} setLoading={setCreateLoading} />
      </GlassModal>
      <Activity mode={globalLoading ? "visible" : "hidden"}>
        <Loader />
      </Activity>
    </>
  )
}

export default AlertsList