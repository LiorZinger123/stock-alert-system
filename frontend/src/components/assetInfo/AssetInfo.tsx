import type{ AssetDetails } from "../../utils/interfaces";
import './assetInfo.scss';

interface AssetInfoProps {
  data: AssetDetails;
}

const AssetInfo = ({ data }: AssetInfoProps) => {
  return (
    <div className="asset-info-container">
      <div className="asset-header">
        <h2>{data.name}</h2>
        <span className="asset-symbol">{data.symbol}</span>
      </div>
      <div className="asset-data">
        <p>Exchange: <strong>{data.exchange ?? 'N/A'}</strong></p>
        <p>Sector: <strong>{data.sector ?? 'N/A'}</strong></p>
        <p>Industry: <strong>{data.industry ?? 'N/A'}</strong></p>
        <p>Current Price: <strong>{data.price != null ? `$${data.price}` : 'N/A'}</strong></p>
      </div>
      {data.user_alerts && data.user_alerts.length > 0 && (
        <div className="alerts-wrapper">
          <h3>Active Alerts ({data.user_alerts.length})</h3>
          {data.user_alerts.map((alert) => (
            <div key={alert.id} className="alert-card">
              <p>Condition: {alert.condition}</p>
              <p>Target: <strong>{alert.target_price}</strong></p>
              <span className={`status-badge ${alert.status.toLowerCase()}`}>
                Status: {alert.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AssetInfo;