import { useState, useEffect, useRef, Activity } from "react";
import { useNavigate } from "react-router-dom";
import Loader from "../Loader/Loader";
import AssetInfo from "../assetInfo/AssetInfo";
import AlertsList from "../alertsList/AlertsList";
import AssetSearchBar from "../assetSearchBar/AssetSearchBar";
import { RiLogoutCircleRLine } from "react-icons/ri";
import { GlassModal } from "../../shared/MuiComponents";
import { logoutUser } from "../../services/api/authService";
import type { SearchedAsset } from "../../utils/interfaces";
import { useLoadingStore } from "../../store/useLoadingStore";
import { useInfiniteAlerts } from "../../services/queries/alertQueries";
import { useAssetDetails, useAssetPrice } from "../../services/queries/assetQueries";
import './dashboard.scss';

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedAsset, setSelectedAsset] = useState<SearchedAsset | null>(null);
  const [isAssetDialogOpen, setIsAssetDialogOpen] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);
  
  const dialogOpenedRef = useRef(false);

  const { isLoading: isGlobalLoading, setIsLoading } = useLoadingStore();

  const { status, isFetchingNextPage } = useInfiniteAlerts();

  const { data: assetDetails, isLoading: isDetailsLoading, isSuccess: isAssetDataSuccess } = useAssetDetails(
    selectedAsset?.symbol ?? "", 
    selectedAsset?.name ?? ""
  );

  const { data: priceData, isLoading: isPriceLoading } = useAssetPrice(selectedAsset?.symbol, isAssetDataSuccess);

  const handleAssetChange = (asset: SearchedAsset | null) => {
    setSelectedAsset(asset);
    dialogOpenedRef.current = false;
    if (!asset) setIsAssetDialogOpen(false);
  };

  const logout = async () => {
    try {
      setAuthLoading(true);
      await logoutUser();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      localStorage.setItem('auth_manual_logout', 'true');
      navigate("/login");
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    if (assetDetails && selectedAsset && !dialogOpenedRef.current) {
      setIsAssetDialogOpen(true);
      dialogOpenedRef.current = true;
    }
  }, [assetDetails, selectedAsset]);

   useEffect(() => {
    setIsLoading(status === 'pending' || isFetchingNextPage || isDetailsLoading);
  }, [status, isFetchingNextPage, isDetailsLoading, setIsLoading]);

  return (
    <>
      <div className="dashboard">
        <img src='system_logo.jpg' alt="system logo" className="system-logo" />
        <button className="logout-button" onClick={logout}>
          <RiLogoutCircleRLine />
        </button>
        <div className="dashboard-content">
          <div className="asset-search-bar-wrapper">
            <AssetSearchBar
              key={selectedAsset ? selectedAsset.symbol : 'reset'}
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
      <Activity mode={(isGlobalLoading || authLoading) ? 'visible' : 'hidden'}>
        <Loader />
      </Activity>
    </>
  );
};

export default Dashboard;