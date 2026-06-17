import { Activity, useState } from "react";
import Loader from "../Loader/Loader";
import AlertRow from "../alertRow/AlertRow";
import NewAlertForm from "../newAlertForm/NewAlertForm";
import { GlassModal } from "../../shared/MuiComponents";
import { useGetAlerts } from "../../services/queries/alertQueries";
import './alertsList.scss';

const AlertsList = () => {
  const { data: alerts, isLoading, error } = useGetAlerts();
  const [createLoading, setCreateLoading] = useState(false);
  const [openNewAlertDialog, setOpenNewAlertDialog] = useState(false);
  const [isPendingUpdate, setIsPendingUpdate] = useState(false);
  const [isPendingDelete, setIsPendingDelete] = useState(false);
  
  const globalLoading = isPendingUpdate || isPendingDelete || createLoading || isLoading;

  return (
    <>
      <div className="alerts-list-wrapper">
        <div className="alerts-list">
          {error ? (
            <div className="error-alerts-state">
              <div className="icon">⚠️</div>
              <p>Failed to load your alerts.</p>
            </div>
          ) : alerts && alerts.length > 0 ? (
            alerts.map((alert) => (
              <AlertRow 
                key={alert.id} 
                alert={alert} 
                setIsPendingUpdate={setIsPendingUpdate} 
                setIsPendingDelete={setIsPendingDelete} 
              />
            ))
          ) : (
            <div className="empty-alerts-state">
              <div className="icon">🔔</div>
              <p>No alerts set for this user.</p>
            </div>
          )}
        </div>
        <button className="add-alert-btn" onClick={() => setOpenNewAlertDialog(true)}>
          ADD NEW ALERT
        </button>
      </div>
      <GlassModal open={openNewAlertDialog} onClose={() => setOpenNewAlertDialog(false)}>
        <NewAlertForm onClose={() => setOpenNewAlertDialog(false)} setLoading={setCreateLoading} />
      </GlassModal>
      <Activity mode={globalLoading ? "visible" : "hidden"}>
        <Loader />
      </Activity>
    </>
  );
};

export default AlertsList;
