// tests/activity.test.js
const request = require('supertest');
const mongoose = require('mongoose');
const Activity = require('../src/models/Activity');

// Import the Express app without connecting to MongoDB
// (we'll handle the connection in the test setup)
let app;

// Setup test database
beforeAll(async () => {
  // If there's already a connection, disconnect first
  if (mongoose.connection.readyState !== 0) {
    await mongoose.disconnect();
  }
  
  const testMongoUri = process.env.TEST_MONGODB_URI || 'mongodb://localhost:27017/activity-logs-test';
  await mongoose.connect(testMongoUri);
  
  // Only require the app after we've set up the test database connection
  // This prevents the app from connecting to the default database
  const express = require('express');
  const cors = require('cors');
  const morgan = require('morgan');
  const activityRoutes = require('../src/routes/activity');
  
  // Create a test app instance
  app = express();
  app.use(cors());
  app.use(express.json());
  app.use(morgan('dev'));
  app.use('/api/activities', activityRoutes);
});

// Clear test database between tests
beforeEach(async () => {
  await Activity.deleteMany({});
});

// Close database connection after tests
afterAll(async () => {
  await mongoose.disconnect();
});

describe('Activity Logs API', () => {
  
  // Test creating a new activity log
  describe('POST /api/activities', () => {
    it('should create a new activity log', async () => {
      const activityData = {
        userId: 'user123',
        action: 'login',
        details: { browser: 'Chrome', os: 'Windows' }
      };
      
      const response = await request(app)
        .post('/api/activities')
        .send(activityData)
        .expect(201);
      
      expect(response.body.userId).toBe(activityData.userId);
      expect(response.body.action).toBe(activityData.action);
      expect(response.body.details).toEqual(activityData.details);
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('_id');
    });
    
    it('should return 400 if required fields are missing', async () => {
      const invalidData = {
        // Missing userId
        action: 'login'
      };
      
      await request(app)
        .post('/api/activities')
        .send(invalidData)
        .expect(400);
    });
  });
  
  // Test retrieving activity logs
  describe('GET /api/activities', () => {
    it('should retrieve all activity logs with pagination', async () => {
      // Insert some test data
      const activities = [
        { userId: 'user1', action: 'login' },
        { userId: 'user2', action: 'profile_update' },
        { userId: 'user1', action: 'logout' }
      ];
      
      await Activity.insertMany(activities);
      
      const response = await request(app)
        .get('/api/activities')
        .expect(200);
      
      expect(response.body.data).toHaveLength(3);
      expect(response.body.pagination).toHaveProperty('total', 3);
    });
    
    it('should respect pagination parameters', async () => {
      // Insert more test data
      const activities = Array(15).fill().map((_, i) => ({ 
        userId: `user${i}`, 
        action: 'login' 
      }));
      
      await Activity.insertMany(activities);
      
      const response = await request(app)
        .get('/api/activities?page=2&limit=5')
        .expect(200);
      
      expect(response.body.data).toHaveLength(5);
      expect(response.body.pagination).toHaveProperty('total', 15);
      expect(response.body.pagination).toHaveProperty('page', 2);
      expect(response.body.pagination).toHaveProperty('limit', 5);
      expect(response.body.pagination).toHaveProperty('pages', 3);
    });
  });
  
  // Test retrieving user-specific activity logs
  describe('GET /api/activities/user/:userId', () => {
    it('should retrieve activity logs for a specific user', async () => {
      // Insert test data
      const activities = [
        { userId: 'user1', action: 'login' },
        { userId: 'user1', action: 'profile_update' },
        { userId: 'user2', action: 'login' }
      ];
      
      await Activity.insertMany(activities);
      
      const response = await request(app)
        .get('/api/activities/user/user1')
        .expect(200);
      
      expect(response.body.data).toHaveLength(2);
      expect(response.body.data[0].userId).toBe('user1');
      expect(response.body.data[1].userId).toBe('user1');
    });
  });
  
  // Test retrieving activity logs by action
  describe('GET /api/activities/action/:action', () => {
    it('should retrieve activity logs for a specific action', async () => {
      // Insert test data
      const activities = [
        { userId: 'user1', action: 'login' },
        { userId: 'user2', action: 'login' },
        { userId: 'user1', action: 'logout' }
      ];
      
      await Activity.insertMany(activities);
      
      const response = await request(app)
        .get('/api/activities/action/login')
        .expect(200);
      
      expect(response.body.data).toHaveLength(2);
      expect(response.body.data[0].action).toBe('login');
      expect(response.body.data[1].action).toBe('login');
    });
  });
  
  // Test retrieving activity logs by date range
  describe('GET /api/activities/range', () => {
    it('should retrieve activity logs within a date range', async () => {
      // Insert test data with different dates
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      
      const twoDaysAgo = new Date();
      twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
      
      const activities = [
        { userId: 'user1', action: 'login', timestamp: new Date() },
        { userId: 'user2', action: 'login', timestamp: yesterday },
        { userId: 'user3', action: 'login', timestamp: twoDaysAgo },
        { userId: 'user4', action: 'login', timestamp: threeDaysAgo }
      ];
      
      await Activity.insertMany(activities);
      
      // Format dates for query string
      const startDate = twoDaysAgo.toISOString();
      const endDate = yesterday.toISOString();
      
      const response = await request(app)
        .get(`/api/activities/range?startDate=${startDate}&endDate=${endDate}`)
        .expect(200);
      
      expect(response.body.data).toHaveLength(2);
    });
    
    it('should return 400 if date parameters are missing', async () => {
      await request(app)
        .get('/api/activities/range')
        .expect(400);
    });
  });
  
  // Test retrieving a specific activity log
  describe('GET /api/activities/:id', () => {
    it('should retrieve a specific activity log by ID', async () => {
      // Insert a test activity
      const activity = new Activity({
        userId: 'user1',
        action: 'login'
      });
      
      await activity.save();
      
      const response = await request(app)
        .get(`/api/activities/${activity._id}`)
        .expect(200);
      
      expect(response.body.userId).toBe('user1');
      expect(response.body.action).toBe('login');
    });
    
    it('should return 404 if activity log is not found', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      
      await request(app)
        .get(`/api/activities/${nonExistentId}`)
        .expect(404);
    });
  });
  
  // Test cleanup functionality
  describe('DELETE /api/activities/cleanup/:days', () => {
    it('should delete activity logs older than specified days', async () => {
      // Insert test data with different dates
      const today = new Date();
      
      const fiveDaysAgo = new Date();
      fiveDaysAgo.setDate(fiveDaysAgo.getDate() - 5);
      
      const tenDaysAgo = new Date();
      tenDaysAgo.setDate(tenDaysAgo.getDate() - 10);
      
      const activities = [
        { userId: 'user1', action: 'login', timestamp: today },
        { userId: 'user2', action: 'login', timestamp: fiveDaysAgo },
        { userId: 'user3', action: 'login', timestamp: tenDaysAgo }
      ];
      
      await Activity.insertMany(activities);
      
      // Delete logs older than 7 days
      const response = await request(app)
        .delete('/api/activities/cleanup/7')
        .expect(200);
      
      expect(response.body.deletedCount).toBe(1); // Only the 10-day old log
      
      // Verify remaining count
      const remainingCount = await Activity.countDocuments();
      expect(remainingCount).toBe(2);
    });
    
    it('should return 400 for invalid days parameter', async () => {
      await request(app)
        .delete('/api/activities/cleanup/invalid')
        .expect(400);
    });
  });
});