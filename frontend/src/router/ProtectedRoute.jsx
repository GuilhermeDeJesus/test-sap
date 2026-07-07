import { Navigate, useLocation } from "react-router-dom";
import { authStore } from "../store/authStore";

export default function ProtectedRoute({ children }) {
  const token = authStore((state) => state.token);
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}
