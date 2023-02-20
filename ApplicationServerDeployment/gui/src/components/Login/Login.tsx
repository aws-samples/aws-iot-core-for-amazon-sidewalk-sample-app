import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { apiClient, setAuthHeader } from "../../apiClient";
import { ENDPOINTS } from "../../endpoints";
import "./styles.css";

interface Props {
  onLoginSuccess: () => void;
}

export const Login = ({ onLoginSuccess }: Props) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isloggingIn, setisLogginIn] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setisLogginIn(true);
    try {
      const response = await apiClient.post<string>(ENDPOINTS.login, {
        username,
        password,
      });
      setAuthHeader(response.data);
      onLoginSuccess();
    } catch (error) {
      console.log({ error });
      toast.error("User or password incorrect")
    } finally {
      setisLogginIn(false);
    }
  };

  return (
    <div className="full-height-with-header flex-abs-center">
      <form className="form-wrapper" onSubmit={handleSubmit}>
        <label>
          Username
          <input
            name="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button type="submit" disabled={isloggingIn}>
          Login
        </button>
      </form>
    </div>
  );
};
