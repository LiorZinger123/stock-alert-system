import api from "./api";
import type { Alert, CreateNewAlertData, UpdateAlertFormData } from "../../utils/interfaces";

export const getUserAlerts = async (): Promise<Alert[]> => {
    const res = await api.get('/alerts');
    return res.data
};

export const createNewAlert = async (data: CreateNewAlertData): Promise<Alert> => {
    const res = await api.post("/alerts", data);
    return res.data;
}

export const updateUserAlert = (
  alertId: number,
  data: UpdateAlertFormData
): Promise<void> => {
  return api.put(`/alerts/${alertId}`, data);
};

export const deleteUserAlert = (alertId: number): Promise<void> => {
  return api.delete(`/alerts/${alertId}`);
};