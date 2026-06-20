import { useEffect, useRef } from "react";
import { useAuthStore } from "../store/useAuthStore";
import { webSocketMessageTypes, wsBaseUrl } from "../utils/constants";
import { updateAlertInCache } from "../services/queries/alertQueries";

export const useWebSocket = () => {
  const { userId } = useAuthStore();
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!userId) return;

    socket.current = new WebSocket(`${wsBaseUrl}/ws/alerts/${userId}`);

    socket.current.onopen = () => {
      console.log("WebSocket Connected!");
    };

    socket.current.onmessage = (event) => {
      try {
        const { type, data } = JSON.parse(event.data);

        switch (type) {
          case webSocketMessageTypes.alertStatus:
            updateAlertInCache(data.alert_id, data.status);
            break;
          default:
            console.warn("Unhandled message type:", type);
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    socket.current.onclose = () => {
      console.log("WebSocket Disconnected");
    };

    socket.current.onerror = (err) => {
      console.error("WebSocket Error:", err);
    };

    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, [userId]);
};
