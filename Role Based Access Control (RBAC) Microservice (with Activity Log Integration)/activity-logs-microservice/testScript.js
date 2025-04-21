// testScript.js
// This script can be used to populate the service with sample data and test the endpoints

const axios = require('axios');

const API_URL = 'http://localhost:3000/api';

// Sample users
const users = ['user123', 'admin456', 'guest789'];

// Sample actions
const actions = [
  'login', 
  'logout', 
  'profile_update', 
  'password_change', 
  'account_creation', 
  'failed_login'
];

// Create random activity log
const createRandomActivity = () => {
  const userId = users[Math.floor(Math.random() * users.length)];
  const action = actions[Math.floor(Math.random() * actions.length)];
  
  // Create a random date within the last 14 days
  const timestamp = new Date();
  timestamp.setDate(timestamp.getDate() - Math.floor(Math.random() * 14));
  
  return {
    userId,
    action,
    timestamp,
    details: {
      browser: ['Chrome', 'Firefox', 'Safari'][Math.floor(Math.random() * 3)],
      os: ['Windows', 'MacOS', 'Linux'][Math.floor(Math.random() * 3)]
    },
    status: Math.random() > 0.2 ? 'success' : 'failure'  // 80% success rate
  };
};

// Create multiple activity logs
const createMultipleActivities = async (count) => {
  console.log(`Creating ${count} random activity logs...`);
  
  for (let i = 0; i < count; i++) {
    try {
      const activity = createRandomActivity();
      await axios.post(`${API_URL}/activities`, activity);
      process.stdout.write('.');  // Show progress
    } catch (error) {
      console.error('Error creating activity:', error.message);
    }
  }
  
  console.log('\nDone creating activities!');
};

// Fetch all activities
const fetchAllActivities = async () => {
  try {
    console.log('\nFetching all activities:');
    const response = await axios.get(`${API_URL}/activities`);
    console.log(`Total activities: ${response.data.pagination.total}`);
    console.log('Sample activities:');
    console.log(JSON.stringify(response.data.data.slice(0, 3), null, 2));
  } catch (error) {
    console.error('Error fetching activities:', error.message);
  }
};

// Fetch activities for a specific user
const fetchUserActivities = async (userId) => {
  try {
    console.log(`\nFetching activities for user: ${userId}`);
    const response = await axios.get(`${API_URL}/activities/user/${userId}`);
    console.log(`Total activities for user: ${response.data.pagination.total}`);
    console.log('Sample activities:');
    console.log(JSON.stringify(response.data.data.slice(0, 3), null, 2));
  } catch (error) {
    console.error('Error fetching user activities:', error.message);
  }
};

// Fetch activities by action type
const fetchActionActivities = async (action) => {
  try {
    console.log(`\nFetching activities for action: ${action}`);
    const response = await axios.get(`${API_URL}/activities/action/${action}`);
    console.log(`Total ${action} activities: ${response.data.pagination.total}`);
    console.log('Sample activities:');
    console.log(JSON.stringify(response.data.data.slice(0, 3), null, 2));
  } catch (error) {
    console.error('Error fetching action activities:', error.message);
  }
};

// Fetch activities within date range
const fetchDateRangeActivities = async (startDate, endDate) => {
  try {
    console.log(`\nFetching activities between ${startDate} and ${endDate}`);
    const response = await axios.get(
      `${API_URL}/activities/range?startDate=${startDate}&endDate=${endDate}`
    );
    console.log(`Total activities in range: ${response.data.pagination.total}`);
    console.log('Sample activities:');
    console.log(JSON.stringify(response.data.data.slice(0, 3), null, 2));
  } catch (error) {
    console.error('Error fetching date range activities:', error.message);
  }
};

// Test cleanup functionality
const testCleanup = async (days) => {
  try {
    console.log(`\nCleaning up activities older than ${days} days`);
    const response = await axios.delete(`${API_URL}/activities/cleanup/${days}`);
    console.log(`Deleted ${response.data.deletedCount} old activities`);
  } catch (error) {
    console.error('Error cleaning up activities:', error.message);
  }
};

// Main function to run all tests
const runTests = async () => {
  // First create sample data
  await createMultipleActivities(30);
  
  // Then run all queries
  await fetchAllActivities();
  await fetchUserActivities('user123');
  await fetchActionActivities('login');
  
  // Get date 7 days ago for date range test
  const endDate = new Date().toISOString();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 7);
  await fetchDateRangeActivities(startDate.toISOString(), endDate);
  
  // Test cleanup
  await testCleanup(10);
  
  console.log('\nAll tests completed!');
};

// Run all tests
runTests().catch(error => {
  console.error('Test script failed:', error.message);
});