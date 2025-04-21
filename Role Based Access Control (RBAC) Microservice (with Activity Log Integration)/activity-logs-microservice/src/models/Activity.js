// src/models/Activity.js
const mongoose = require('mongoose');

const activitySchema = new mongoose.Schema({
  userId: {
    type: String,
    required: true,
    index: true
  },
  action: {
    type: String,
    required: true,
    enum: ['login', 'logout', 'profile_update', 'password_change', 'account_creation', 'account_deletion', 'permission_change', 'failed_login', 'other']
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  },
  ipAddress: {
    type: String
  },
  userAgent: {
    type: String
  },
  details: {
    type: mongoose.Schema.Types.Mixed
  },
  resourceType: {
    type: String
  },
  resourceId: {
    type: String
  },
  status: {
    type: String,
    enum: ['success', 'failure', 'pending'],
    default: 'success'
  }
});

// Create compound indexes for common queries
activitySchema.index({ userId: 1, timestamp: -1 });
activitySchema.index({ action: 1, timestamp: -1 });

const Activity = mongoose.model('Activity', activitySchema);

module.exports = Activity;