import React, { useRef, useEffect, useState } from "react";
import AlertRow from "../alertRow/AlertRow";
import NewAlertForm from "../newAlertForm/NewAlertForm";
import { GlassModal } from "../../shared/MuiComponents";
import { useLoadingStore } from "../../store/useLoadingStore";
import { useInfiniteAlerts } from "../../services/queries/alertQueries";
import "./alertsList.scss";

const AlertsList = () => {
  const { setIsLoading } = useLoadingStore();
  const [openNewAlertDialog, setOpenNewAlertDialog] = useState(false);

  const loadMoreRef = useRef<HTMLDivElement>(null);
  const alertListRef = useRef<HTMLDivElement>(null);
  const previousAlertsCountRef = useRef(0);
  const previousPagesCountRef = useRef(0);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, status } =
    useInfiniteAlerts();

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    });

    const currentTarget = loadMoreRef.current;
    if (currentTarget) observer.observe(currentTarget);

    return () => {
      if (currentTarget) observer.unobserve(currentTarget);
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  useEffect(() => {
    if (!data) return;

    const currentTotal = data.pages.reduce((acc, page) => acc + page.length, 0);
    const currentPageCount = data.pages.length;

    if (
      currentTotal > previousAlertsCountRef.current &&
      previousAlertsCountRef.current !== 0 &&
      currentPageCount === previousPagesCountRef.current
    ) {
      alertListRef.current?.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    }

    previousAlertsCountRef.current = currentTotal;
    previousPagesCountRef.current = currentPageCount;
  }, [data]);

  useEffect(() => {
    setIsLoading(status === "pending");
  }, [status, setIsLoading]);

  return (
    <>
      <div className="alerts-list-wrapper">
        <div className="alerts-list" ref={alertListRef}>
          {status === "pending" ? null : status === "error" ? (
            <div className="error-alerts-state">
              <div className="icon">⚠️</div>
              <p>Failed to load alerts</p>
            </div>
          ) : data?.pages[0]?.length === 0 ? (
            <div className="empty-alerts-state">
              <div className="icon">🔔</div>
              <p>No alerts set for this user.</p>
            </div>
          ) : (
            data?.pages.map((page, i) => (
              <React.Fragment key={i}>
                {page.map((alert) => (
                  <AlertRow key={alert.id} alert={alert} />
                ))}
              </React.Fragment>
            ))
          )}
          <div ref={loadMoreRef} />
        </div>
        <button
          className="add-alert-btn"
          onClick={() => setOpenNewAlertDialog(true)}
        >
          ADD NEW ALERT
        </button>
      </div>
      <GlassModal
        open={openNewAlertDialog}
        onClose={() => setOpenNewAlertDialog(false)}
      >
        <NewAlertForm onClose={() => setOpenNewAlertDialog(false)} />
      </GlassModal>
    </>
  );
};

export default AlertsList;
