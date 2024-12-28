
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function NotificationList() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await axios.get('/api/v1/notifications');
        setNotifications(response.data);
      } catch (error) {
        console.error('Error fetching notifications:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-center p-4">Loading notifications...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-bold mb-4">Notifications</h2>
      <div className="space-y-2">
        {notifications.map((notification, index) => (
          <div key={index} className="p-3 border rounded bg-gray-50">
            <div className="font-medium">{notification.type}</div>
            <div className="text-sm text-gray-600">
              {notification.data.euro_amount} EUR → {notification.data.gold_grams} g
            </div>
            <div className="text-xs text-gray-500">
              {new Date(notification.data.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
        {notifications.length === 0 && (
          <p className="text-gray-500 text-center">No notifications yet</p>
        )}
      </div>
    </div>
  );
}
