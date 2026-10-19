// Decky integration adapted from @decky/rollup 1.0.2 (BSD-3-Clause).
// Copyright (c) 2024, Steam Deck Homebrew. See THIRD_PARTY_NOTICES.md.
import { readFileSync, rmSync } from "node:fs";
import commonjs from "@rollup/plugin-commonjs";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import externalGlobals from "rollup-plugin-external-globals";

const manifest = JSON.parse(readFileSync(new URL("./plugin.json", import.meta.url), "utf8"));
const dist = new URL("./dist/", import.meta.url);

export default {
  input: "src/index.tsx",
  context: "window",
  external: ["react", "react-dom", "@decky/ui"],
  treeshake: "smallest",
  plugins: [
    { name: "clean-dist", buildStart: () => rmSync(dist, { recursive: true, force: true }) },
    typescript({
      compilerOptions: { rootDir: "src" },
      exclude: ["**/*.test.ts", "**/*.test.tsx", "**/test/**"],
    }),
    commonjs(),
    nodeResolve({ browser: true }),
    externalGlobals({
      react: "SP_REACT",
      "react/jsx-runtime": "SP_JSX",
      "react-dom": "SP_REACTDOM",
      "@decky/ui": "DFL",
      "@decky/manifest": JSON.stringify(manifest),
    }),
    replace({
      preventAssignment: true,
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV || "production"),
    }),
  ],
  output: {
    dir: "dist",
    format: "esm",
    exports: "default",
    sourcemap: true,
    sourcemapPathTransform: (path) =>
      path.replace(/^\.\.\//, `decky://decky/plugin/${encodeURIComponent(manifest.name)}/`),
  },
};
