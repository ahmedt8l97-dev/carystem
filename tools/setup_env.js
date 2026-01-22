const fs = require('fs');
const path = require('path');

const envLocalPath = path.join(__dirname, '..', '.env');
const envPath = path.join(__dirname, '..', 'web-frontend', '.env');

try {
    if (fs.existsSync(envLocalPath)) {
        const content = fs.readFileSync(envLocalPath, 'utf8');
        const lines = content.split('\n');
        let convexUrl = '';

        for (const line of lines) {
            if (line.startsWith('CONVEX_URL=')) {
                convexUrl = line.split('=')[1].trim();
                break;
            }
        }

        if (convexUrl) {
            // Write to .env for Vite
            const viteEnvContent = `VITE_CONVEX_URL=${convexUrl}\n`;
            fs.writeFileSync(envPath, viteEnvContent);
            console.log(`Success: Wrote VITE_CONVEX_URL to .env: ${convexUrl}`);
        } else {
            console.log("Error: CONVEX_URL not found in .env");
        }
    } else {
        console.log("Error: .env not found at root.");
    }
} catch (e) {
    console.error("Error setting up env:", e);
}
