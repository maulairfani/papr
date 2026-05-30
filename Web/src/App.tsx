import { Route, Routes } from "react-router-dom";
import { Workspace } from "./pages/Workspace";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Workspace />} />
    </Routes>
  );
}
