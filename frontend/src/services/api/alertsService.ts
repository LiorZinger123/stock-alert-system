import api from "./api";
import type { Alert, CreateNewAlertData, UpdateAlertFormData } from "../../utils/interfaces";

export const fetchAlertsPaginated = async (
  offset: number,
  limit: number = 5, 
): Promise<Alert[]> => {
  const { data } = await api.get<Alert[]>("/alerts", {
    params: {
      offset,
      limit,
    },
  });
  return data;
};

export const createNewAlert = async (data: CreateNewAlertData): Promise<Alert> => {
  const res = await api.post("/alerts", data);
  return res.data;
}

export const updateUserAlert = async (
  alertId: number, 
  data: UpdateAlertFormData
): Promise<Alert> => {
  const response = await api.put(`/alerts/${alertId}`, data);
  return response.data; 
};

export const deleteUserAlert = (alertId: number): Promise<void> => {
  return api.delete(`/alerts/${alertId}`);
};