import { definePlugin } from "@decky/api";
import { staticClasses } from "@decky/ui";
import { FaPuzzlePiece } from "react-icons/fa";
import { App } from "./App";
export default definePlugin(() => ({
  name: "DeckyMods",
  titleView: <div className={staticClasses.Title}>DeckyMods</div>,
  content: <App />,
  icon: <FaPuzzlePiece />,
  // Native file pickers temporarily hide QAM. Preserve the pending result owner.
  alwaysRender: true,
}));
