const fs = require('fs');
const path = require('path');
const { ConvexHttpClient } = require("convex/browser");
const { api } = require("./convex/_generated/api");
require("dotenv").config({ path: ".env.local" });

const client = new ConvexHttpClient(process.env.CONVEX_URL);

async function migrate() {
    console.log("Starting migration...");

    // Migrate Products
    const cachePath = path.join(__dirname, 'backend', 'telegram_cache.json');
    if (fs.existsSync(cachePath)) {
        const data = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
        const products = Object.values(data);

        console.log(`Found ${products.length} products to migrate.`);

        for (const p of products) {
            try {
                // Map fields from Python JSON to Convex Schema
                // Python: product_number, product_name, car_name, model_number, type, quantity, price_iqd, wholesale_price_iqd, image (url)

                await client.mutation(api.products.addProduct, {
                    product_number: p.product_number,
                    product_name: p.product_name,
                    car_name: p.car_name,
                    model_number: p.model_number || "",
                    type: p.type || "Other",
                    quantity: p.quantity || 0,
                    original_quantity: p.original_quantity || p.quantity,
                    price_iqd: p.price_iqd || 0,
                    wholesale_price_iqd: p.wholesale_price_iqd || 0,
                    image: p.image || undefined,
                });
                console.log(`Migrated: ${p.product_name}`);
            } catch (e) {
                console.error(`Failed to migrate ${p.product_number}:`, e.message);
            }
        }
    } else {
        console.log("No telegram_cache.json found.");
    }

    console.log("Migration complete.");
}

migrate().catch(console.error);
