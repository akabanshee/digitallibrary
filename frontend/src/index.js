import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const rootElement = document.getElementById("root");
if (!rootElement) {
  console.error("Root element bulunamadı. index.html dosyanızı kontrol edin.");
}

const root = ReactDOM.createRoot(rootElement)