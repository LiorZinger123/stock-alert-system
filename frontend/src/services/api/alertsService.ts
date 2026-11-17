import api from "./api";
import type {
  Alert,
  CreateNewAlertData,
  UpdateAlertFormData,
} from "../../utils/interfaces";
import { alertsPaginatedLimit } from "../../utils/constants";

export const fetchAlertsPaginated = async (cursorId?: number) => {
  const { data } = await api.get<Alert[]>("/alerts", {
    params: {
      cursor_id: cursorId,
      limit: alertsPaginatedLimit,
    },
  });
  return data;
};

export const createNewAlert = async (
  data: CreateNewAlertData,
): Promise<Alert> => {
  const res = await api.post("/alerts", data);
  return res.data;
};

export const updateUserAlert = async (
  alertId: number,
  data: UpdateAlertFormData,
): Promise<Alert> => {
  const response = await api.put(`/alerts/${alertId}`, data);
  return response.data;
};

export const deleteUserAlert = (alertId: number): Promise<void> => {
  return api.delete(`/alerts/${alertId}`);
};
