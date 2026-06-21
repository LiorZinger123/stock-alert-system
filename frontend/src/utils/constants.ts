import type { AlertCondition, AlertStatus } from "./interfaces";

export const alertConditionMap: Record<AlertCondition, string> = {
  above: "Above (>=)",
  below: "Below (<=)",
};

export const conditionOptions = (
  Object.keys(alertConditionMap) as AlertCondition[]
).map((key) => ({
  label: alertConditionMap[key],
  value: key,
}));

export const updateAlertStatusOptions = [
  { label: "Active", value: "active" },
  { label: "Inactive", value: "inactive" },
];

export const alertStatusMap: Record<AlertStatus, string> = {
  active: "active",
  inactive: "inactive",
  pending: "pending",
  sent: "sent",
  failed: "failed",
};

export const webSocketMessageTypes: Record<string, string> = {
  alertStatus: "ALERT_STATUS_UPDATE",
  priceChange: "PRICE_CHANGE_UPDATE",
};

export const backendBaseUrl = "http://localhost:8000";
export const wsBaseUrl = backendBaseUrl.replace(/^http/, "ws");

export const localStorageManualLogout = "auth_manual_logout";
