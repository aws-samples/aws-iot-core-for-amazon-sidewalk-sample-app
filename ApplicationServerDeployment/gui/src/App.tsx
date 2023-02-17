// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Header } from "./components/Header/Header";
import { DevicesWrapper } from "./components/DevicesWrapper/DevicesWrapper";
import { Login } from "./components/Login/Login";
import { useEffect, useState } from "react";
import { ACCESS_TOKEN } from "./constants";
import "./App.css";

function App() {
  const [isUserLoggedIn, setisLogginIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const handleLoginSuccess = () => {
    setisLogginIn(true);
  };

  useEffect(() => {
    const accessToken = localStorage.getItem(ACCESS_TOKEN);

    if (accessToken) {
      setisLogginIn(true);
    }

    setIsLoading(false);
  }, []);

  if (isLoading) {
    return <></>;
  }

  return (
    <div className="App">
      <Header />
      {isUserLoggedIn ? (
        <DevicesWrapper />
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;
