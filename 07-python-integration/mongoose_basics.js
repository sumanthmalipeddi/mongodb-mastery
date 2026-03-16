/**
 * Mongoose Basics — MongoDB with Node.js
 * =======================================
 * This file is for MERN stack learners. Python developers can skip this.
 *
 * Covers: Schema definition, models, CRUD, middleware, virtuals, population.
 *
 * Usage:
 *   npm install mongoose dotenv
 *   node mongoose_basics.js
 */

require("dotenv").config({ path: "../.env" });
const mongoose = require("mongoose");

// =========================================================================
// CONNECTION
// =========================================================================

async function connect() {
  const uri = process.env.MONGODB_URI;
  if (!uri) {
    console.error("❌ Set MONGODB_URI in your .env file first!");
    process.exit(1);
  }

  try {
    await mongoose.connect(uri);
    console.log("✅ Connected to MongoDB with Mongoose!\n");
  } catch (err) {
    console.error("❌ Connection failed:", err.message);
    process.exit(1);
  }
}

// =========================================================================
// SCHEMA DEFINITION
// =========================================================================

// Schemas define the structure and validation for documents.
// This is a key difference from PyMongo — Mongoose enforces schema at the app level.

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, "Name is required"], // Custom error message
      trim: true, // Remove whitespace
      minlength: 2,
      maxlength: 50,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true, // Auto-convert to lowercase
      match: [/^\S+@\S+\.\S+$/, "Invalid email format"],
    },
    age: {
      type: Number,
      min: [0, "Age cannot be negative"],
      max: 150,
    },
    role: {
      type: String,
      enum: ["user", "admin", "moderator"], // Only these values allowed
      default: "user",
    },
    hobbies: [String], // Array of strings
    address: {
      // Nested object
      street: String,
      city: String,
      state: String,
    },
    isActive: {
      type: Boolean,
      default: true,
    },
  },
  {
    timestamps: true, // Adds createdAt and updatedAt automatically
  }
);

// =========================================================================
// VIRTUAL FIELDS (computed, not stored in DB)
// =========================================================================

userSchema.virtual("profile").get(function () {
  return `${this.name} (${this.email}) - ${this.role}`;
});

// Ensure virtuals are included when converting to JSON
userSchema.set("toJSON", { virtuals: true });

// =========================================================================
// MIDDLEWARE (Pre/Post Hooks)
// =========================================================================

// Runs before save — like a trigger
userSchema.pre("save", function (next) {
  console.log(`  [middleware] About to save: ${this.name}`);
  next();
});

// Runs after save
userSchema.post("save", function (doc) {
  console.log(`  [middleware] Saved: ${doc.name} (${doc._id})`);
});

// =========================================================================
// INSTANCE METHODS
// =========================================================================

userSchema.methods.greet = function () {
  return `Hello, I'm ${this.name} and I'm a ${this.role}`;
};

// =========================================================================
// STATIC METHODS
// =========================================================================

userSchema.statics.findByRole = function (role) {
  return this.find({ role });
};

// =========================================================================
// CREATE MODEL
// =========================================================================

const User = mongoose.model("User", userSchema);

// =========================================================================
// BLOG POST SCHEMA (for demonstrating population/references)
// =========================================================================

const postSchema = new mongoose.Schema({
  title: { type: String, required: true },
  content: String,
  author: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User", // Reference to User model
    required: true,
  },
  tags: [String],
  createdAt: { type: Date, default: Date.now },
});

const Post = mongoose.model("Post", postSchema);

// =========================================================================
// MAIN — CRUD Operations
// =========================================================================

async function main() {
  await connect();

  // Clean up from previous runs
  await User.deleteMany({});
  await Post.deleteMany({});

  // --- CREATE ---
  console.log("=" .repeat(50));
  console.log("CREATE");
  console.log("=".repeat(50));

  // Method 1: new + save (triggers middleware)
  const alice = new User({
    name: "Alice Johnson",
    email: "alice@example.com",
    age: 29,
    role: "admin",
    hobbies: ["reading", "coding"],
    address: { street: "123 Main St", city: "Portland", state: "OR" },
  });
  await alice.save();

  // Method 2: Model.create (shorthand)
  const bob = await User.create({
    name: "Bob Smith",
    email: "bob@example.com",
    age: 34,
    hobbies: ["gaming", "cooking"],
  });

  const carol = await User.create({
    name: "Carol Williams",
    email: "carol@example.com",
    age: 27,
    role: "moderator",
  });

  // --- READ ---
  console.log("\n" + "=".repeat(50));
  console.log("READ");
  console.log("=".repeat(50));

  // findById
  const found = await User.findById(alice._id);
  console.log(`\n  findById: ${found.name} (${found.role})`);

  // findOne
  const admin = await User.findOne({ role: "admin" });
  console.log(`  findOne admin: ${admin.name}`);

  // find with chaining
  const youngUsers = await User.find({ age: { $lt: 30 } })
    .sort({ age: 1 })
    .select("name age -_id") // Only these fields
    .lean(); // Returns plain objects instead of Mongoose documents
  console.log("  Users under 30:", youngUsers);

  // Using virtual
  console.log(`  Virtual profile: ${alice.profile}`);

  // Using instance method
  console.log(`  Greet: ${alice.greet()}`);

  // Using static method
  const admins = await User.findByRole("admin");
  console.log(`  Admins: ${admins.map((u) => u.name).join(", ")}`);

  // --- UPDATE ---
  console.log("\n" + "=".repeat(50));
  console.log("UPDATE");
  console.log("=".repeat(50));

  // findByIdAndUpdate (returns the old document by default)
  const updated = await User.findByIdAndUpdate(
    bob._id,
    { $set: { age: 35 }, $push: { hobbies: "running" } },
    { new: true } // Return the updated document
  );
  console.log(`\n  Updated Bob: age=${updated.age}, hobbies=${updated.hobbies}`);

  // updateMany
  const result = await User.updateMany({}, { $set: { isActive: true } });
  console.log(`  updateMany: modified ${result.modifiedCount} documents`);

  // --- POPULATION (like $lookup / JOIN) ---
  console.log("\n" + "=".repeat(50));
  console.log("POPULATION (References)");
  console.log("=".repeat(50));

  // Create posts with author references
  await Post.create([
    { title: "MongoDB Guide", content: "Learn MongoDB...", author: alice._id, tags: ["mongodb", "tutorial"] },
    { title: "Node.js Tips", content: "Useful Node tips...", author: alice._id, tags: ["nodejs"] },
    { title: "Cooking 101", content: "Best recipes...", author: bob._id, tags: ["cooking"] },
  ]);

  // Populate replaces the ObjectId reference with the actual document
  const posts = await Post.find()
    .populate("author", "name email") // Only include name and email from author
    .sort({ createdAt: -1 });

  console.log("\n  Posts with populated authors:");
  for (const post of posts) {
    console.log(`  "${post.title}" by ${post.author.name} (${post.author.email})`);
  }

  // --- DELETE ---
  console.log("\n" + "=".repeat(50));
  console.log("DELETE");
  console.log("=".repeat(50));

  const deleted = await User.findByIdAndDelete(carol._id);
  console.log(`\n  Deleted: ${deleted.name}`);

  const remaining = await User.countDocuments();
  console.log(`  Remaining users: ${remaining}`);

  // --- VALIDATION EXAMPLE ---
  console.log("\n" + "=".repeat(50));
  console.log("VALIDATION");
  console.log("=".repeat(50));

  try {
    await User.create({ name: "X", email: "bad-email", age: -5, role: "hacker" });
  } catch (err) {
    console.log("\n  Validation errors caught:");
    for (const [field, error] of Object.entries(err.errors || {})) {
      console.log(`    ${field}: ${error.message}`);
    }
  }

  // Cleanup and disconnect
  await mongoose.connection.close();
  console.log("\n✅ Done! Disconnected from MongoDB.");
}

main().catch(console.error);
