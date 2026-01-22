import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const createBackup = mutation({
    args: {
        filename: v.string(),
        data: v.string(),
        total_products: v.number(),
        type: v.string(),
    },
    handler: async (ctx, args) => {
        return await ctx.db.insert("backups", {
            ...args,
            created_at: new Date().toISOString(),
        });
    },
});

export const getBackups = query({
    handler: async (ctx) => {
        return await ctx.db
            .query("backups")
            .withIndex("by_created_at")
            .order("desc")
            .take(50);
    },
});

export const deleteOldBackups = mutation({
    args: { keepCount: v.number() },
    handler: async (ctx, args) => {
        const all = await ctx.db.query("backups").order("desc").collect();
        if (all.length > args.keepCount) {
            const toDelete = all.slice(args.keepCount);
            for (const b of toDelete) {
                await ctx.db.delete(b._id);
            }
        }
    }
});
