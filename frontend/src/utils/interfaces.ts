export interface LoginFormInputs {
  username: string;
  password: string;
}

export interface RegisterFormInputs extends LoginFormInputs {
  email: string
}

export type AlertCondition = "above" | "below";

interface Asset {
  symbol: string;
  name?: string;
  sector?: string;
  industry?: string;
  exchange?: string;
  current_price?: number;
}

type AlertStatus = "active" | "inactive" | "pending" | "sent" | "failed"

export interface Alert {
  id: number;
  target_price: number;
  condition: AlertCondition;
  status: AlertStatus;
  asset: Asset;
  created_at?: Date;
  triggered_at?: Date;
  triggered_price?: number;
}

export interface SearchedAsset {
  symbol: string;
  name: string;
}

export interface NewAlertFromAsset {
  symbol: string;
  name: string;
}

export interface NewAlertFormValues {
  asset: NewAlertFromAsset | null;
  targetPrice: string;
  condition: string;
};

export interface CreateNewAlertData {
  symbol: string;
  target_price: number;
  condition: AlertCondition;
}

export interface UpdateAlertFormValues {
  targetPrice: string;
  condition: AlertCondition;
  status: AlertStatus;
}

export interface UpdateAlertFormData {
  target_price: number;
  condition: AlertCondition;
  status: AlertStatus;
}
