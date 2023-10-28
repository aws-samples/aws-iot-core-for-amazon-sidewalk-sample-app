// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Header } from "./components/Header/Header";
import { Suspense, useEffect } from "react";
import "./App.css";
import { Spinner } from "./components/Spinner/Spinner";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import { Routes } from "./routes";

function App() {
  const { isAuthorized } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthorized) {
      navigate(Routes.sensorMonitoring);
    } else {
      navigate(Routes.auth);
    }

  }, [isAuthorized]);

  return (
    <div className="App">
      <Header />
      <Suspense fallback={<Spinner />}>
        <Outlet />
      </Suspense>
    </div>
  );
}

export default App;
