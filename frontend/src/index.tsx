import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { QueryClientProvider } from "@tanstack/react-query";
import App from "./App.tsx";
import { queryClient } from "./lib/queryClient.ts";
import "./index.scss";
import "./utils/globals.scss";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </GoogleOAuthProvider>
  </StrictMode>,
);
