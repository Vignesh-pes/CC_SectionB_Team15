// server.js
require('dotenv').config(); // Load environment variables from .env file
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const { createClient } = require('@supabase/supabase-js');

// Check if Supabase credentials are loaded
if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY) {
    console.error("Error: Supabase URL or Anon Key not found in .env file");
    process.exit(1); // Stop the server if credentials are missing
}

// Initialize Supabase client
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(cors()); // Enable Cross-Origin Resource Sharing for requests from your frontend
app.use(express.json()); // Enable parsing of JSON request bodies

// Basic Route to check if server is running
app.get('/', (req, res) => {
    res.send('Auth Backend is running!');
});


// --- Authentication Route ---
// --- Authentication Route (Custom Table Version) ---
app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;

    // ** --- GET THESE NAMES FROM YOUR FRIEND --- **
    const USER_TABLE_NAME = 'users'; // Replace with actual table name (e.g., 'users', 'profiles')
    const EMAIL_COLUMN = 'email'; // Replace with actual email column name
    const PASSWORD_HASH_COLUMN = 'password'; // Replace with actual password hash column name
    // ** ----------------------------------------- **

    if (!email || !password) {
        return res.status(400).json({ error: 'Email and password are required' });
    }

    try {
        // 1. Fetch user data from the custom table based on email
        const { data: user, error: queryError } = await supabase
            .from(USER_TABLE_NAME)
            .select(`*, ${PASSWORD_HASH_COLUMN}`) // Select all columns AND explicitly the password hash column
            .eq(EMAIL_COLUMN, email)
            .single(); // .single() expects 0 or 1 result. Throws error if multiple found.

        // Handle potential errors during DB query
        if (queryError && queryError.code !== 'PGRST116') { // PGRST116 = 'Searched item was not found' which is okay here
           console.error('Supabase query error:', queryError);
           return res.status(500).json({ error: 'Database error during login' });
        }

        // 2. Check if user exists
        if (!user) {
           console.log(`Login attempt failed: User not found for email: ${email}`);
           // Use a generic message for security (don't reveal if email exists)
           return res.status(401).json({ error: 'Invalid credentials' });
        }

        // 3. Compare the provided password with the stored hash
        // Ensure the password hash column exists on the fetched user object
        const storedHash = user[PASSWORD_HASH_COLUMN];
        if (!storedHash) {
            console.error(`Error: Password hash column '${PASSWORD_HASH_COLUMN}' not found on user object for email: ${email}`);
            return res.status(500).json({ error: 'Server configuration error' });
        }

        const passwordMatch = await bcrypt.compare(password, storedHash);

        if (passwordMatch) {
            // 4. Passwords match - Login successful!
            console.log(`Login successful for: ${user[EMAIL_COLUMN]}`);

            // IMPORTANT: Do NOT send the password hash back to the client!
            // Create a user object without the password hash.
            const { [PASSWORD_HASH_COLUMN]: removedHash, ...userDataToSend } = user;

            res.status(200).json({ message: 'Login successful', user: userDataToSend });
        } else {
            // 5. Passwords do not match
            console.log(`Login attempt failed: Incorrect password for email: ${email}`);
            return res.status(401).json({ error: 'Invalid credentials' });
        }

    } catch (err) {
        console.error('Server error during login:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// --- End of Authentication Route ---

// Start the server
app.listen(port, () => {
    console.log(`Auth backend server listening at http://localhost:${port}`);
});