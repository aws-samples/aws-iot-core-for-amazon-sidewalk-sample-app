import { Navigate, createBrowserRouter } from "react-router-dom";
import App from "./App";
import { Login } from "./Views/Login/Login";
import { SensorMonitoring } from "./Views/SensorMonitoring/SensorMonitoring";
import { FirmwareOta } from "./Views/FirmwareOta/FirmwareOta";

export enum Routes {
  auth = "/auth",
  sensorMonitoring = "/sensor-monitoring",
  firmwareOTA = "/firmware-ota",
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    ErrorBoundary: () => <div>There was an error</div>,
    children: [
      {
        path: Routes.auth,
        element: <Login />,
      },
      {
        path: Routes.sensorMonitoring,
        element: <SensorMonitoring />,
      },
      {
        path: Routes.firmwareOTA,
        element: <FirmwareOta />,
      },
      {
        path: "*",
        element: <Navigate to={Routes.auth} replace />,
      },
    ],
  },
]);
