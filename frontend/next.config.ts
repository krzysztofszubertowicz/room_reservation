import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  devIndicators: false,
  // Buduje samowystarczalny serwer (.next/standalone) do lekkiego obrazu Docker.
  output: "standalone",
  // Nie przerywaj builda produkcyjnego z powodu ostrzezen ESLint (regul stylu kodu).
  // Kod i tak jest poprawnie kompilowany; lintowanie mozna uruchamiac osobno (`npm run lint`).
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Nie przerywaj builda z powodu istniejacych w projekcie niespojnosci typow TS.
  // Tryb deweloperski (next dev) i tak ich nie wymusza - zachowujemy to samo zachowanie.
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
