import { ConvexHttpClient } from "convex/browser";
export const convex = new ConvexHttpClient(import.meta.env.VITE_CONVEX_URL || "https://flexible-lion-950.convex.cloud");
