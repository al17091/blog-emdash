import { readFile, mkdir } from "node:fs/promises";
import { resolve } from "node:path";

import { Kysely } from "kysely";

import { runMigrations } from "emdash/db";
import { createDialect as createPostgresDialect } from "emdash/db/postgres";
import { createDialect as createSqliteDialect } from "emdash/db/sqlite";
import { applySeed, validateSeed } from "emdash/seed";
import { LocalStorage } from "emdash/storage/local";

function parseArgs(argv) {
	const args = {
		seedPath: null,
		onConflict: "update",
		includeContent: true,
		uploadsDir: "./uploads",
		mediaBaseUrl: "/_emdash/api/media/file",
		skipMediaDownload: false,
	};

	for (let i = 0; i < argv.length; i++) {
		const token = argv[i];
		if (!token) continue;

		if (token === "--seed" && argv[i + 1]) {
			args.seedPath = argv[++i];
			continue;
		}
		if (token === "--on-conflict" && argv[i + 1]) {
			args.onConflict = argv[++i];
			continue;
		}
		if (token === "--no-content") {
			args.includeContent = false;
			continue;
		}
		if (token === "--uploads-dir" && argv[i + 1]) {
			args.uploadsDir = argv[++i];
			continue;
		}
		if (token === "--media-base-url" && argv[i + 1]) {
			args.mediaBaseUrl = argv[++i];
			continue;
		}
		if (token === "--skip-media-download") {
			args.skipMediaDownload = true;
			continue;
		}
	}

	return args;
}

async function resolveSeedPath(explicitSeedPath) {
	if (explicitSeedPath) return resolve(process.cwd(), explicitSeedPath);

	const pkgPath = resolve(process.cwd(), "package.json");
	try {
		const pkg = JSON.parse(await readFile(pkgPath, "utf-8"));
		if (pkg?.emdash?.seed) return resolve(process.cwd(), pkg.emdash.seed);
	} catch {
		// ignore
	}

	return resolve(process.cwd(), "seed/seed.json");
}

async function main() {
	const args = parseArgs(process.argv.slice(2));
	const dbEngine = (process.env.EMDASH_DB ?? "sqlite").toLowerCase();
	const onConflict = args.onConflict;

	if (!["skip", "update", "error"].includes(onConflict)) {
		console.error(`Invalid --on-conflict value: ${onConflict}`);
		console.log("Use: skip, update, or error");
		process.exit(1);
	}

	const seedPath = await resolveSeedPath(args.seedPath);
	console.log(`Seed file: ${seedPath}`);

	console.log("Loading seed file...");
	const seed = JSON.parse(await readFile(seedPath, "utf-8"));
	console.log("Loaded");

	console.log("Validating seed file...");
	const validation = validateSeed(seed);
	if (!validation.valid) {
		console.error("Seed file is invalid");
		for (const err of validation.errors) console.error(err);
		process.exit(1);
	}
	console.log("Seed file is valid");

	const uploadsDir = resolve(process.cwd(), args.uploadsDir);
	await mkdir(uploadsDir, { recursive: true });
	const storage = new LocalStorage({ directory: uploadsDir, baseUrl: args.mediaBaseUrl });

	let dialect;
	if (dbEngine === "postgres" || dbEngine === "pg") {
		dialect = createPostgresDialect({ connectionString: process.env.DATABASE_URL });
		console.log("Database: postgres (via env DATABASE_URL / PG*)");
	} else {
		const sqliteUrl = process.env.EMDASH_DATABASE_URL ?? "file:./data.db";
		dialect = createSqliteDialect({ url: sqliteUrl });
		console.log(`Database: sqlite (${sqliteUrl})`);
	}

	const db = new Kysely({
		dialect,
	});

	try {
		console.log("Running migrations...");
		const { applied } = await runMigrations(db);
		if (applied.length > 0) {
			console.log(`Applied ${applied.length} migrations`);
		} else {
			console.log("Database up to date");
		}

		console.log("Applying seed...");
		const result = await applySeed(db, seed, {
			includeContent: args.includeContent,
			onConflict,
			storage,
			skipMediaDownload: args.skipMediaDownload,
		});

		console.log("Done!");
		console.log(
			`Collections: ${result.collections.created} created, ${result.collections.skipped} skipped, ${result.collections.updated} updated`,
		);
		console.log(
			`Fields: ${result.fields.created} created, ${result.fields.skipped} skipped, ${result.fields.updated} updated`,
		);
		console.log(
			`Content: ${result.content.created} created, ${result.content.skipped} skipped, ${result.content.updated} updated`,
		);
	} finally {
		await db.destroy();
	}
}

await main();
