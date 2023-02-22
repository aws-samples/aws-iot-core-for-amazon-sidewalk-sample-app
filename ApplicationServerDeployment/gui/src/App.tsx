// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Header } from "./components/Header/Header";
import { DevicesWrapper } from "./components/DevicesWrapper/DevicesWrapper";
import { Login } from "./components/Login/Login";
import { useEffect, useState } from "react";
import { ACCESS_TOKEN, UNAUTHORIZE } from "./constants";
import "./App.css";
import { toast } from "react-hot-toast";

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

  // check for auth error var to show a message in case user gets logged out
  useEffect(() => {
    if (localStorage.getItem(UNAUTHORIZE)) {
      setTimeout(() => {
        toast.error("Unauthorize error");
        localStorage.removeItem(UNAUTHORIZE);
      }, 0);
    }
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
