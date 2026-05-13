import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

// React 入口只负责挂载根组件，业务状态统一收敛在 App 和 hooks 中。
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
