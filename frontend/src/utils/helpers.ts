import type { Alert } from '../utils/interfaces';

export const isDuplicateAlert = (
  alerts: Alert[], 
  newAssetSymbol: string, 
  newPrice: number, 
  newCondition: string,
  excludeId?: number
): boolean => {
  return alerts.some(alert => 
    alert.asset.symbol === newAssetSymbol &&
    alert.target_price === newPrice &&
    alert.condition === newCondition &&
    alert.id !== excludeId
  );
};