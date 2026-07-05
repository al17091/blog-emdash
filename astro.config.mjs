import node from "@astrojs/node";
import react from "@astrojs/react";
import { defineConfig, fontProviders } from "astro/config";
import emdash, { local } from "emdash/astro";
import { postgres, sqlite } from "emdash/db";

const dbEngine = (process.env['EMDASH_DB'] ?? "sqlite").toLowerCase();
const emdashDatabase =
	dbEngine === "postgres" || dbEngine === "pg"
		? // Avoid baking secrets into the build: prefer runtime env vars.
			// If DATABASE_URL is not present at build time, keep the config empty so
			// node-postgres can fall back to env (DATABASE_URL / PG*).
			postgres(process.env['DATABASE_URL'] ? { connectionString: process.env['DATABASE_URL'] } : {})
		: sqlite({ url: process.env['EMDASH_DATABASE_URL'] ?? "file:./data.db" });

export default defineConfig({
	output: "server",
	security: {
		// Disable origin check to allow the same Docker image (built once) 
		// to be deployed across multiple environments (e.g., STG, PROD) with different hostnames.
		// CSRF protection relies on infrastructure-level routing and EmDash session auth.
		checkOrigin: false,
	},
	adapter: node({
		mode: "standalone",
	}),
	image: {
		layout: "constrained",
		responsiveStyles: true,
	},
	integrations: [
		react(),
		emdash({
			database: emdashDatabase,
			storage: local({
				directory: "./uploads",
				baseUrl: "/_emdash/api/media/file",
			}),
			plugins: [],
		}),
	],
	fonts: [
		{
			provider: fontProviders.google(),
			name: "Inter",
			cssVariable: "--font-sans",
			weights: [400, 500, 600, 700],
			fallbacks: ["sans-serif"],
		},
		{
			provider: fontProviders.google(),
			name: "JetBrains Mono",
			cssVariable: "--font-mono",
			weights: [400, 500],
			fallbacks: ["monospace"],
		},
	],
	devToolbar: { enabled: false },
});
