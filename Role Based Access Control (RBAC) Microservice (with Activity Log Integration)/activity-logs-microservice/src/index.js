// src/index.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const morgan = require('morgan');
require('dotenv').config();

const activityRoutes = require('./routes/activity');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/api/activities', activityRoutes);

// Home route
app.get('/', (req, res) => {
  res.json({ message: 'Activity Logs Microservice is running' });
});

// Only connect to the database and start the server if this file is run directly
// This prevents connection issues when importing for tests
if (require.main === module) {
  // Database connection
  mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/activity-logs')
    .then(() => {
      console.log('Connected to MongoDB');
      // Start server
      app.listen(PORT, () => {
        console.log(`Server is running on port ${PORT}`);
      });
    })
    .catch(err => console.error('Could not connect to MongoDB', err));
}

module.exports = app; // For testing