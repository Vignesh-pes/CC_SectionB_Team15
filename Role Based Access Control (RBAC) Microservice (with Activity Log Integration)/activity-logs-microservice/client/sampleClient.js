// client/sampleClient.js
// A minimal React application to demonstrate the Activity Logs API

import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

const API_URL = 'http://localhost:3000/api';

// Activity Log Item Component
const ActivityLogItem = ({ activity }) => {
  // Format the timestamp
  const formattedDate = new Date(activity.timestamp).toLocaleString();
  
  // Determine status color
  const statusColor = activity.status === 'success' ? 'green' : 
                     activity.status === 'failure' ? 'red' : 'orange';
  
  return (
    <div style={{ 
      border: '1px solid #ddd', 
      padding: '10px', 
      marginBottom: '10px',
      borderRadius: '4px',
      backgroundColor: '#f9f9f9'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong>User: {activity.userId}</strong>
        <span style={{ color: statusColor }}>{activity.status}</span>
      </div>
      
      <div>
        <span>Action: <strong>{activity.action}</strong></span>
      </div>
      
      <div>
        <small>{formattedDate}</small>
      </div>
      
      {activity.ipAddress && (
        <div><small>IP: {activity.ipAddress}</small></div>
      )}
      
      {activity.details && (
        <div style={{ 
          marginTop: '5px', 
          padding: '5px', 
          backgroundColor: '#eee', 
          borderRadius: '3px',
          fontSize: '0.8em'
        }}>
          <pre style={{ margin: 0 }}>
            {JSON.stringify(activity.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

// Activity Log Filter Component
const ActivityLogFilter = ({ onFilter }) => {
  const [userId, setUserId] = useState('');
  const [action, setAction] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onFilter({ userId, action });
  };
  
  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        <input 
          type="text" 
          placeholder="Filter by User ID" 
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          style={{ padding: '8px', flex: 1 }}
        />
        
        <select 
          value={action} 
          onChange={(e) => setAction(e.target.value)}
          style={{ padding: '8px' }}
        >
          <option value="">All Actions</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="profile_update">Profile Update</option>
          <option value="password_change">Password Change</option>
          <option value="account_creation">Account Creation</option>
          <option value="failed_login">Failed Login</option>
          <option value="permission_change">Permission Change</option>
        </select>
        
        <button 
          type="submit"
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#4285f4', 
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Filter
        </button>
        
        <button 
          type="button"
          onClick={() => {
            setUserId('');
            setAction('');
            onFilter({});
          }}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#f5f5f5', 
            border: '1px solid #ddd',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Reset
        </button>
      </div>
    </form>
  );
};

// Activity Logs App
const ActivityLogsApp = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 });
  
  // Load activities based on current filters and pagination
  const loadActivities = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/activities?page=${pagination.page}&limit=${pagination.limit}`;
      
      // Apply filters if they exist
      if (filters.userId) {
        url = `${API_URL}/activities/user/${filters.userId}?page=${pagination.page}&limit=${pagination.limit}`;
      } else if (filters.action) {
        url = `${API_URL}/activities/action/${filters.action}?page=${pagination.page}&limit=${pagination.limit}`;
      }
      
      const response = await axios.get(url);
      
      setActivities(response.data.data);
      setPagination({
        ...pagination,
        total: response.data.pagination.total,
        pages: response.data.pagination.pages
      });
      
    } catch (err) {
      setError('Failed to load activity logs. ' + err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Load activities on initial mount and when filters/pagination change
  useEffect(() => {
    loadActivities();
  }, [filters, pagination.page, pagination.limit]);
  
  // Handle filter changes
  const handleFilter = (newFilters) => {
    setPagination({ ...pagination, page: 1 }); // Reset to first page on filter change
    setFilters(newFilters);
  };
  
  // Handle pagination
  const handlePageChange = (newPage) => {
    setPagination({ ...pagination, page: newPage });
  };
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>Activity Logs</h1>
      
      <ActivityLogFilter onFilter={handleFilter} />
      
      {loading ? (
        <div>Loading activity logs...</div>
      ) : error ? (
        <div style={{ color: 'red' }}>{error}</div>
      ) : activities.length === 0 ? (
        <div>No activity logs found.</div>
      ) : (
        <>
          <div>
            {activities.map((activity) => (
              <ActivityLogItem key={activity._id} activity={activity} />
            ))}
          </div>
          
          {/* Pagination controls */}
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            margin: '20px 0',
            gap: '5px'
          }}>
            <button 
              onClick={() => handlePageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
              style={{ padding: '5px 10px' }}
            >
              Previous
            </button>
            
            <span style={{ padding: '5px 10px' }}>
              Page {pagination.page} of {pagination.pages || 1}
            </span>
            
            <button 
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.pages}
              style={{ padding: '5px 10px' }}
            >
              Next
            </button>
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <small>Total records: {pagination.total}</small>
          </div>
        </>
      )}
    </div>
  );
};

// Render the app
ReactDOM.render(
  <ActivityLogsApp />,
  document.getElementById('root')
);

// Note: To use this client, you would need to set up a React application
// with the necessary dependencies and a proper build setup.
// This is just a demonstration of how a client might interact with the API.