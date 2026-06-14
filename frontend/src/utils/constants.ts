import type { AlertCondition } from "./interfaces";

export const alertConditionMap: Record<AlertCondition, string> = {
  above: "Above (>=)",
  below: "Below (<=)",
};

export const conditionOptions = (Object.keys(alertConditionMap) as AlertCondition[]).map((key) => ({
  label: alertConditionMap[key],
  value: key,
}));

export const updateAlertStatusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
];
