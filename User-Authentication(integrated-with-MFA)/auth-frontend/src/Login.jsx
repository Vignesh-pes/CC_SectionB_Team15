// src/Login.jsx
import React, { useState } from 'react';
import axios from 'axios';

function Login() {
    // Existing state for password login
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState(''); // For login form messages

    // State to manage login/MFA flow
    const [isPasswordVerified, setIsPasswordVerified] = useState(false); // Track password success
    const [userEmail, setUserEmail] = useState(''); // Store logged-in user's email for MFA

    // MFA Specific State
    const [showMfaSection, setShowMfaSection] = useState(false); // Controls visibility of OTP input area
    const [otp, setOtp] = useState(''); // Stores the OTP entered by the user
    const [mfaMessage, setMfaMessage] = useState(''); // For MFA status messages
    const [isFullyLoggedIn, setIsFullyLoggedIn] = useState(false); // Final state after MFA success

    // --- 1. Handle Initial Password Login ---
    const handleSubmit = async (event) => {
        event.preventDefault();
        setMessage('');
        setMfaMessage('');
        setIsPasswordVerified(false);
        setIsFullyLoggedIn(false);
        setShowMfaSection(false);


        try {
            // Call your Node.js auth backend (Task 1)
            const response = await axios.post('/api/auth/login', {
                email: email,
                password: password,
            });

            console.log('Password Login successful:', response.data);
            // Password is correct! Prepare for MFA step.
            setUserEmail(response.data.user?.email); // Store email from successful login
            setIsPasswordVerified(true); // Mark password as verified
            setMessage(''); // Clear any previous login errors

        } catch (error) {
             console.error('Login error:', error);
             if (error.response) {
                 setMessage(`Login failed: ${error.response.data.error || 'Invalid credentials'}`);
             } else if (error.request) {
                 setMessage('Login failed: Could not connect to the auth server.');
             } else {
                 setMessage(`Login failed: ${error.message}`);
             }
             setIsPasswordVerified(false);
             setPassword('');
        }
    };

    // --- 2. Handle MFA Initiation ---
    const handleInitiateMfa = async () => {
        if (!userEmail) {
            setMfaMessage('Error: User email not found.');
            return;
        }
        setMfaMessage('Sending OTP...');
        setShowMfaSection(false); // Hide OTP input initially

        try {
            // Call Friend's MFA Service Endpoint (Original Flask/MySQL version)
            const response = await axios.post('http://localhost:5000/generate-otp', { // Adjust URL if needed
                email: userEmail
            });

            console.log('Generate OTP response:', response.data);
            setMfaMessage('OTP sent successfully to your email. Please check and enter it below.');
            setShowMfaSection(true); // Show the OTP input section

        } catch (error) {
            console.error('Generate OTP error:', error);
            setShowMfaSection(false);
             if (error.response) {
                 setMfaMessage(`Failed to send OTP: ${error.response.data.message || 'MFA Server error'}`);
            } else if (error.request) {
                setMfaMessage('Failed to send OTP: Cannot reach MFA service. Is it running?');
            } else {
                setMfaMessage(`Failed to send OTP: ${error.message}`);
            }
        }
    };

    // --- 3. Handle MFA Verification ---
    const handleVerifyOtp = async (event) => {
        event.preventDefault();
        setMfaMessage('Verifying OTP...');

        if (!userEmail || !otp) {
            setMfaMessage('Email or OTP missing.');
            return;
        }

        try {
            // Call Friend's MFA Service Endpoint (Original Flask/MySQL version)
            // !!! THIS '/verify-otp' ENDPOINT MUST BE IMPLEMENTED BY YOUR FRIEND !!!
            const response = await axios.post('http://localhost:5000/verify-otp', { // Adjust URL if needed
                email: userEmail,
                otp: otp
            });

            console.log('Verify OTP response:', response.data);
            // Assuming success means the friend's service returns a 200 OK
            // and potentially a message like {'message': 'Verification successful'}
            setMfaMessage('MFA Verification Successful! Access Granted.');
            setIsFullyLoggedIn(true); // Set final login state
            setShowMfaSection(false); // Hide MFA section after success


        } catch (error) {
            console.error('Verify OTP error:', error);
             if (error.response) {
                 // Assuming friend implements 400/401 for invalid/expired OTP
                 setMfaMessage(`Verification failed: ${error.response.data.message || 'Invalid or expired OTP'}`);
             } else if (error.request) {
                 setMfaMessage('Verification failed: Cannot reach MFA service.');
             } else {
                setMfaMessage(`Verification failed: ${error.message}`);
            }
            setIsFullyLoggedIn(false);
            setOtp(''); // Clear OTP input on failure
        }
    };

    // --- 4. Render Logic ---
    return (
        <div>
            <h2>Login</h2>

            {/* Show Login Form if password is not yet verified */}
            {!isPasswordVerified && !isFullyLoggedIn && (
                 <form onSubmit={handleSubmit}>
                     <div>
                         <label htmlFor="email">Email:</label>
                         <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                     </div>
                     <div>
                         <label htmlFor="password">Password:</label>
                         <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                     </div>
                     <button type="submit">Login</button>
                     {message && <p style={{ color: 'red' }}>{message}</p>}
                 </form>
            )}

            {/* Show Initiate MFA button if password IS verified but MFA isn't done */}
            {isPasswordVerified && !showMfaSection && !isFullyLoggedIn && (
                <div>
                    <p>Password verified! Click below to send MFA code to {userEmail}.</p>
                    <button onClick={handleInitiateMfa}>Send MFA Code</button>
                    {mfaMessage && <p>{mfaMessage}</p>}
                </div>
            )}

             {/* Show MFA input section if OTP has been initiated */}
            {isPasswordVerified && showMfaSection && !isFullyLoggedIn && (
                 <div>
                     <h3>Enter MFA Code</h3>
                     <p>{mfaMessage || `Enter the OTP sent to ${userEmail}.`}</p>
                     <form onSubmit={handleVerifyOtp}>
                         <div>
                             <label htmlFor="otp">OTP:</label>
                             <input type="text" id="otp" value={otp} onChange={(e) => setOtp(e.target.value)} required maxLength="6"/>
                         </div>
                         <button type="submit">Verify OTP</button>
                     </form>
                </div>
            )}

            {/* Show final success message */}
            {isFullyLoggedIn && (
                 <div>
                     <h3 style={{ color: 'green' }}>Login and MFA Successful!</h3>
                     <p>Welcome, {userEmail}!</p>
                     {/* You can add navigation or display user content here */}
                 </div>
            )}
        </div>
    );
}

export default Login;