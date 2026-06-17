import { Activity, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Loader from "../Loader/Loader";
import AssetInfo from "../assetInfo/AssetInfo";
import AlertsList from "../alertsList/AlertsList";
import AssetSearchBar from "../assetSearchBar/AssetSearchBar";
import { RiLogoutCircleRLine } from "react-icons/ri";
import { GlassModal } from "../../shared/MuiComponents";
import { logoutUser } from "../../services/api/authService";
import type { SearchedAsset } from "../../utils/interfaces";
import { useAssetDetails } from "../../services/queries/assetQueries";
import './dashboard.scss';

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedAsset, setSelectedAsset] = useState<SearchedAsset | null>(null);
  const [isAssetDialogOpen, setIsAssetDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const dialogOpenedRef = useRef(false);

  const { data: assetDetails, isLoading: isDetailsLoading } = useAssetDetails(
    selectedAsset?.symbol ?? "", 
    selectedAsset?.name ?? ""
  );

  const handleAssetChange = (asset: SearchedAsset | null) => {
    setSelectedAsset(asset);
    dialogOpenedRef.current = false;

    if (!asset) {
      setIsAssetDialogOpen(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      await logoutUser();
    } catch (error: unknown) {
      console.error("Logout failed:", error);
    } finally {
      localStorage.setItem('auth_manual_logout', 'true');
      navigate("/login");
      setLoading(false);
    }
  };

  useEffect(() => {
    if (assetDetails && selectedAsset && !dialogOpenedRef.current) {
      setIsAssetDialogOpen(true);
      dialogOpenedRef.current = true;
    }
  }, [assetDetails, selectedAsset]);

  return (
    <>
      <div className="dashboard">
        <img src='system_logo.jpg' alt="system logo" className="system-logo" />
        <div className="dashboard-content">
          <div className="asset-search-bar-logout-wrapper">
            <AssetSearchBar
              key={selectedAsset ? selectedAsset.symbol : 'reset'}
              value={selectedAsset}
              onChange={handleAssetChange}
              label="Search Asset Info"
            />
            <button className="logout-button" onClick={logout}>
              <RiLogoutCircleRLine />
            </button>
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
            <AssetInfo data={assetDetails} />
          )}
        </GlassModal>
      </div>
      <Activity mode={loading || isDetailsLoading ? 'visible' : 'hidden'}>
        <Loader />
      </Activity>
    </>
  );
};

export default Dashboard;