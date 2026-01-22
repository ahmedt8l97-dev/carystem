import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Helper to hash password client-side matching, or server-side verification
// Since we are migrating from python sha256 hex digest, we can replicate it or expect hashed.
// For security, usually hashing is done on client or we use a better method (bcrypt), 
// but to maintain compatibility with the existing system style, we simply compare.
// Note: In a real production app, use crypto.subtle.digest properly or an auth provider!

export const login = mutation({
    args: { username: v.string(), passwordHash: v.string() },
    handler: async (ctx, args) => {
        const user = await ctx.db
            .query("users")
            .withIndex("by_username", (q) => q.eq("username", args.username))
            .first();

        if (!user) {
            return { token: null, error: "Invalid username" };
        }

        // Compare hashes
        if (user.password !== args.passwordHash) {
            return { token: null, error: "Invalid password" };
        }

        // In a full system we'd generate a JWT or session ID. 
        // For this simple migration, we return the user profile.
        // The client will store this state.
        return {
            token: "session_" + Math.random().toString(36).substring(7), // Mock token
            user: {
                username: user.username,
                name: user.name,
                role: user.role,
            }
        };
    },
});

export const createUser = mutation({
    args: {
        username: v.string(),
        passwordHash: v.string(),
        name: v.string(),
        family_name: v.string(),
        photo: v.optional(v.string()),
        role: v.string(),
    },
    handler: async (ctx, args) => {
        const existing = await ctx.db
            .query("users")
            .withIndex("by_username", (q) => q.eq("username", args.username))
            .first();

        if (existing) {
            throw new Error("User already exists");
        }

        const id = await ctx.db.insert("users", {
            username: args.username,
            password: args.passwordHash,
            name: args.name,
            family_name: args.family_name,
            photo: args.photo,
            role: args.role,
            created_at: new Date().toISOString(),
        });

        return id;
    },
});

export const generateUploadUrl = mutation(async (ctx) => {
    return await ctx.storage.generateUploadUrl();
});

export const listUsers = query({
    handler: async (ctx) => {
        return await ctx.db.query("users").collect();
    }
});

export const createSession = mutation({
    args: {
        token: v.string(),
        username: v.string(),
        role: v.string(),
        expires_at: v.string(),
    },
    handler: async (ctx, args) => {
        await ctx.db.insert("sessions", args);
    }
});

export const verifySession = query({
    args: { token: v.string() },
    handler: async (ctx, args) => {
        const session = await ctx.db
            .query("sessions")
            .withIndex("by_token", (q) => q.eq("token", args.token))
            .first();

        if (!session) return null;

        // Check expiry
        if (new Date(session.expires_at) < new Date()) {
            return null;
        }

        return {
            username: session.username,
            role: session.role,
        };
    }
});

export const deleteSession = mutation({
    args: { token: v.string() },
    handler: async (ctx, args) => {
        const session = await ctx.db
            .query("sessions")
            .withIndex("by_token", (q) => q.eq("token", args.token))
            .first();
        if (session) {
            await ctx.db.delete(session._id);
        }
    }
});
