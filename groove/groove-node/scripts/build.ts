// https://github.com/gjuchault/typescript-library-starter/blob/main/esbuild-hook.js
import path from "path";
import { build as esbuild, BuildOptions } from "esbuild";

const baseConfig: BuildOptions = {
  platform: "node",
  target: "esnext",
  format: "cjs",
  nodePaths: [path.join(__dirname, "../src")],
  sourcemap: true,
  external: [],
  bundle: true,
};

async function main() {
  await esbuild({
    ...baseConfig,
    outdir: path.join(__dirname, "../build/cjs"),
    entryPoints: [
      path.join(__dirname, "../src/index.ts"),
      path.join(__dirname, "../src/install-ca.ts"),
    ],
  });

  await esbuild({
    ...baseConfig,
    format: "esm",
    outdir: path.join(__dirname, "../build/esm"),
    entryPoints: [
      path.join(__dirname, "../src/index.ts"),
      path.join(__dirname, "../src/install-ca.ts"),
    ],
  });
}

if (require.main === module) {
  main();
}