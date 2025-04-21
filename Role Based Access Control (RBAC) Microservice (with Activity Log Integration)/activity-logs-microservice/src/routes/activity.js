// src/routes/activity.js
const express = require('express');
const router = express.Router();
const Activity = require('../models/Activity');

// Middleware to validate request body
const validateActivityLog = (req, res, next) => {
  const { userId, action } = req.body;
  
  if (!userId || !action) {
    return res.status(400).json({ error: 'userId and action are required fields' });
  }
  
  next();
};

// Create a new activity log
router.post('/', validateActivityLog, async (req, res) => {
  try {
    // Extract IP address from request
    const ipAddress = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    
    // Create activity log with IP address and user agent
    const activity = new Activity({
      ...req.body,
      ipAddress,
      userAgent: req.headers['user-agent']
    });
    
    await activity.save();
    res.status(201).json(activity);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Get all activity logs (with pagination)
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    const activities = await Activity.find()
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Activity.countDocuments();
    
    res.json({
      data: activities,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get activity logs for a specific user
router.get('/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    const activities = await Activity.find({ userId })
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Activity.countDocuments({ userId });
    
    res.json({
      data: activities,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get activity logs by action type
router.get('/action/:action', async (req, res) => {
  try {
    const { action } = req.params;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    const activities = await Activity.find({ action })
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Activity.countDocuments({ action });
    
    res.json({
      data: activities,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get activity logs within a date range
router.get('/range', async (req, res) => {
  try {
    const { startDate, endDate } = req.query;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    if (!startDate || !endDate) {
      return res.status(400).json({ error: 'startDate and endDate are required query parameters' });
    }
    
    const query = {
      timestamp: {
        $gte: new Date(startDate),
        $lte: new Date(endDate)
      }
    };
    
    const activities = await Activity.find(query)
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Activity.countDocuments(query);
    
    res.json({
      data: activities,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get a specific activity log by ID
router.get('/:id', async (req, res) => {
  try {
    const activity = await Activity.findById(req.params.id);
    
    if (!activity) {
      return res.status(404).json({ error: 'Activity log not found' });
    }
    
    res.json(activity);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete activity logs older than a certain date (for cleanup)
router.delete('/cleanup/:days', async (req, res) => {
  try {
    const days = parseInt(req.params.days);
    
    if (isNaN(days) || days <= 0) {
      return res.status(400).json({ error: 'Days parameter must be a positive number' });
    }
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const result = await Activity.deleteMany({ timestamp: { $lt: cutoffDate } });
    
    res.json({
      message: `Deleted ${result.deletedCount} activity logs older than ${days} days`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;