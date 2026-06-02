import { Route, Routes } from "react-router-dom";
import { Workspace } from "./pages/Workspace";
import { Design } from "./pages/Design";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Workspace />} />
      {/* Dev-only living style guide for design tokens + primitives. */}
      <Route path="/design" element={<Design />} />
    </Routes>
  );
}
