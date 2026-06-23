import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import AssetInfo from "../assetInfo/AssetInfo";
import AlertsList from "../alertsList/AlertsList";
import AssetSearchBar from "../assetSearchBar/AssetSearchBar";
import { RiLogoutCircleRLine } from "react-icons/ri";
import { GlassModal } from "../../shared/MuiComponents";
import { logoutUser } from "../../services/api/authService";
import type { SearchedAsset } from "../../utils/interfaces";
import { useLoadingStore } from "../../store/useLoadingStore";
import { localStorageManualLogout } from "../../utils/constants";
import { useInfiniteAlerts } from "../../services/queries/alertQueries";
import { useAuthStore, type AuthState } from "../../store/useAuthStore";
import {
  useAssetDetails,
  useAssetPrice,
} from "../../services/queries/assetQueries";
import "./dashboard.scss";

const Dashboard = () => {
  const navigate = useNavigate();
  const { setIsLoading } = useLoadingStore();
  const { clearUser } = useAuthStore((state: AuthState) => state);
  const { status, isFetchingNextPage } = useInfiniteAlerts();
  const [selectedAsset, setSelectedAsset] = useState<SearchedAsset | null>(
    null,
  );
  const [isAssetDialogOpen, setIsAssetDialogOpen] = useState<boolean>(false);
  const dialogOpenedRef = useRef<boolean>(false);

  const {
    data: assetDetails,
    isLoading: isDetailsLoading,
    isSuccess: isAssetDataSuccess,
  } = useAssetDetails(selectedAsset?.symbol ?? "", selectedAsset?.name ?? "");

  const { data: priceData, isLoading: isPriceLoading } = useAssetPrice(
    selectedAsset?.symbol,
    isAssetDataSuccess,
  );

  const handleAssetChange = (asset: SearchedAsset | null): void => {
    setSelectedAsset(asset);
    dialogOpenedRef.current = false;
    if (!asset) setIsAssetDialogOpen(false);
  };

  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      await logoutUser();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      localStorage.setItem(localStorageManualLogout, "true");
      clearUser();
      navigate("/login");
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (assetDetails && selectedAsset && !dialogOpenedRef.current) {
      setIsAssetDialogOpen(true);
      dialogOpenedRef.current = true;
    }
  }, [assetDetails, selectedAsset]);

  useEffect(() => {
    setIsLoading(
      status === "pending" || isFetchingNextPage || isDetailsLoading,
    );
  }, [status, isFetchingNextPage, isDetailsLoading, setIsLoading]);

  return (
    <div className="dashboard">
      <img src="system-logo.jpg" alt="system logo" className="system-logo" />
      <button className="logout-button" onClick={logout}>
        <RiLogoutCircleRLine />
      </button>
      <div className="dashboard-content">
        <div className="asset-search-bar-wrapper">
          <AssetSearchBar
            key={selectedAsset ? selectedAsset.symbol : "reset"}
            value={selectedAsset}
            onChange={handleAssetChange}
            label="Search Asset Info"
          />
        </div>
        <AlertsList />
      </div>
      <GlassModal
        open={isAssetDialogOpen}
        onClose={() => {
          setIsAssetDialogOpen(false);
          setSelectedAsset(null);
        }}
      >
        {assetDetails && (
          <AssetInfo
            data={assetDetails}
            price={priceData}
            isPriceLoading={isPriceLoading}
          />
        )}
      </GlassModal>
    </div>
  );
};

export default Dashboard;
