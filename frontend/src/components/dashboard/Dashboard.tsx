import { useState } from "react";
import AlertsList from "../alertsList/AlertsList"
import AssetSearchBar from "../assetSearchBar/AssetSearchBar"
import type { NewAlertFromAsset } from "../../utils/interfaces";
import './dashboard.scss'
import { GlassModal } from "../../shared/MuiComponents";
import AssetInfo from "../assetInfo/AssetInfo";

const Dashboard = () => {
  const [selectedAsset, setSelectedAsset] = useState<NewAlertFromAsset | null>(null);
  const [isAssetDialogOpen, setIsAssetDialogOpen] = useState(false);

  const handleAssetChange = (asset: NewAlertFromAsset | null) => {
    setSelectedAsset(asset);
    
    if (asset !== null) {
      setIsAssetDialogOpen(true);
    }
  };

  return (
    <div className="dashboard">
      <img src='system_logo.jpg' alt="system logo" className="system-logo" />
      <div className="dashboard-content">
        <div className="asset-search-bar-wrapper">
          <AssetSearchBar value={selectedAsset} onChange={handleAssetChange} label="Search Asset Info" />
        </div>
        <AlertsList />
      </div>
      <GlassModal open={isAssetDialogOpen} onClose={() => setIsAssetDialogOpen(false)}>
        <AssetInfo />
      </GlassModal>
    </div>
  )
}

export default Dashboard