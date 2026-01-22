import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
    users: defineTable({
        username: v.string(),
        password: v.string(), // sha256 hash
        role: v.string(),
        name: v.string(),
        family_name: v.optional(v.string()),
        photo: v.optional(v.string()), // Storage ID or URL
        created_at: v.string(),
    }).index("by_username", ["username"]),

    products: defineTable({
        product_number: v.optional(v.string()),
        product_name: v.string(),
        car_name: v.string(),
        model_number: v.string(),
        type: v.string(),
        quantity: v.number(),
        original_quantity: v.number(),
        price_iqd: v.number(),
        wholesale_price_iqd: v.number(),
        status: v.string(),
        image: v.optional(v.string()),
        last_update: v.string(),
        message_id: v.optional(v.number()),
    })
        .index("by_product_number", ["product_number"])
        .index("by_type", ["type"])
        .index("by_car", ["car_name"]),

    backups: defineTable({
        filename: v.string(),
        data: v.string(), // JSON string of the backup
        created_at: v.string(),
        total_products: v.number(),
        type: v.string(), // manual, daily, weekly
    }).index("by_created_at", ["created_at"]),

    sessions: defineTable({
        token: v.string(),
        username: v.string(),
        role: v.string(),
        expires_at: v.string(),
    }).index("by_token", ["token"]),
});
