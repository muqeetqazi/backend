# Protected Vision API Integration Guide

This guide explains how to integrate the Protected Vision backend API with the React Native frontend. It includes code examples and best practices.

## Authentication

### Setting up the API Client

Create an API client with authentication handling:

```javascript
// app/services/api.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and not already retrying
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });
        
        if (response.status === 200) {
          // Update stored tokens
          await AsyncStorage.setItem('access_token', response.data.access);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, redirect to login
        // Clear tokens
        await AsyncStorage.removeItem('access_token');
        await AsyncStorage.removeItem('refresh_token');
        
        // Handle redirect to login in your app
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### Authentication Service

Create authentication service functions:

```javascript
// app/services/auth.js
import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login/', {
      email,
      password,
    });
    
    // Store tokens
    await AsyncStorage.setItem('access_token', response.data.access);
    await AsyncStorage.setItem('refresh_token', response.data.refresh);
    
    // Store user data
    await AsyncStorage.setItem('user', JSON.stringify({
      id: response.data.id,
      email: response.data.email,
      username: response.data.username,
      first_name: response.data.first_name,
      last_name: response.data.last_name,
      profile_image: response.data.profile_image,
    }));
    
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Login failed' };
  }
};

export const register = async (userData) => {
  try {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Registration failed' };
  }
};

export const logout = async () => {
  await AsyncStorage.removeItem('access_token');
  await AsyncStorage.removeItem('refresh_token');
  await AsyncStorage.removeItem('user');
};

export const getProfile = async () => {
  try {
    const response = await api.get('/auth/profile/');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get profile' };
  }
};

export const updateProfile = async (profileData) => {
  try {
    const response = await api.put('/auth/profile/', profileData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to update profile' };
  }
};

export const getUserPreferences = async () => {
  try {
    const response = await api.get('/auth/preferences/');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get preferences' };
  }
};

export const updateUserPreferences = async (preferences) => {
  try {
    const response = await api.put('/auth/preferences/', preferences);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to update preferences' };
  }
};

export const changePassword = async (oldPassword, newPassword) => {
  try {
    const response = await api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to change password' };
  }
};
```

## Document Management

Create a service for document operations:

```javascript
// app/services/documents.js
import api from './api';

export const getDocuments = async (filters = {}) => {
  try {
    const response = await api.get('/documents/', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get documents' };
  }
};

export const getDocument = async (id) => {
  try {
    const response = await api.get(`/documents/${id}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get document' };
  }
};

export const uploadDocument = async (data) => {
  try {
    // Create form data for file upload
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('file_type', data.fileType);
    
    // Append file
    const fileUri = data.fileUri;
    const fileType = data.fileType;
    const fileName = fileUri.split('/').pop();
    
    formData.append('file', {
      uri: fileUri,
      type: fileType === 'image' ? 'image/jpeg' : fileType === 'video' ? 'video/mp4' : 'application/pdf',
      name: fileName,
    });
    
    const response = await api.post('/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to upload document' };
  }
};

export const deleteDocument = async (id) => {
  try {
    const response = await api.delete(`/documents/${id}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to delete document' };
  }
};

export const getDocumentScans = async (documentId) => {
  try {
    const response = await api.get(`/documents/${documentId}/scans/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get document scans' };
  }
};

export const getAllScans = async (filters = {}) => {
  try {
    const response = await api.get('/documents/scans/', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get all scans' };
  }
};
```

## Sensitive Information Detection

Create a service for document analysis:

```javascript
// app/services/detection.js
import api from './api';

export const analyzeDocument = async (documentId) => {
  try {
    const response = await api.post('/detection/analyze/', {
      document_id: documentId,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to analyze document' };
  }
};

export const getDetectionJobs = async (filters = {}) => {
  try {
    const response = await api.get('/detection/jobs/', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get detection jobs' };
  }
};

export const getDetectionJob = async (id) => {
  try {
    const response = await api.get(`/detection/jobs/${id}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get detection job' };
  }
};

export const getAvailableModels = async () => {
  try {
    const response = await api.get('/detection/models/');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get available models' };
  }
};
```

## Integrating with React Native Components

### Example: Login Screen

```javascript
import React, { useState } from 'react';
import { View, TextInput, Button, Text, StyleSheet, Alert } from 'react-native';
import { login } from '../services/auth';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }
    
    setLoading(true);
    
    try {
      const userData = await login(email, password);
      setLoading(false);
      
      // Navigate to Home screen
      navigation.reset({
        index: 0,
        routes: [{ name: 'Home' }],
      });
    } catch (error) {
      setLoading(false);
      Alert.alert('Error', error.detail || 'Login failed');
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Protected Vision</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <Button
        title={loading ? "Logging in..." : "Login"}
        onPress={handleLogin}
        disabled={loading}
      />
      
      <Text
        style={styles.registerText}
        onPress={() => navigation.navigate('Register')}
      >
        Don't have an account? Register
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ccc',
    marginBottom: 15,
    padding: 10,
    borderRadius: 5,
  },
  registerText: {
    marginTop: 20,
    textAlign: 'center',
    color: 'blue',
  },
});

export default LoginScreen;
```

### Example: Document Upload Screen

```javascript
import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, Alert, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { uploadDocument } from '../services/documents';
import { analyzeDocument } from '../services/detection';

const UploadScreen = ({ navigation }) => {
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  
  const selectMedia = async (type) => {
    try {
      let result;
      
      if (type === 'camera') {
        result = await ImagePicker.launchCameraAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Images,
          allowsEditing: true,
          aspect: [4, 3],
          quality: 1,
        });
      } else {
        result = await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.All,
          allowsEditing: true,
          aspect: [4, 3],
          quality: 1,
        });
      }
      
      if (!result.cancelled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        setSelectedMedia({
          uri: asset.uri,
          type: asset.type === 'video' ? 'video' : 'image',
          width: asset.width,
          height: asset.height,
        });
        
        // Auto-generate title based on timestamp
        setTitle(`Document_${new Date().toISOString().split('T')[0]}`);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to select media');
    }
  };
  
  const handleUpload = async () => {
    if (!selectedMedia || !title) {
      Alert.alert('Error', 'Please select media and enter a title');
      return;
    }
    
    setUploading(true);
    
    try {
      // Upload document
      const documentData = await uploadDocument({
        title,
        fileType: selectedMedia.type,
        fileUri: selectedMedia.uri,
      });
      
      // Analyze the uploaded document
      const analysisResult = await analyzeDocument(documentData.id);
      
      setUploading(false);
      
      // Navigate to results screen
      navigation.navigate('Result', {
        scanId: analysisResult.scan_id,
        documentId: analysisResult.document_id,
      });
    } catch (error) {
      setUploading(false);
      Alert.alert('Error', error.detail || 'Failed to upload and analyze document');
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Upload Document</Text>
      
      {selectedMedia ? (
        <Image
          source={{ uri: selectedMedia.uri }}
          style={styles.preview}
          resizeMode="contain"
        />
      ) : (
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderText}>No media selected</Text>
        </View>
      )}
      
      <View style={styles.buttonContainer}>
        <Button
          title="Select from Gallery"
          onPress={() => selectMedia('gallery')}
          disabled={uploading}
        />
        
        <Button
          title="Take a Photo"
          onPress={() => selectMedia('camera')}
          disabled={uploading}
        />
      </View>
      
      <TextInput
        style={styles.input}
        placeholder="Document Title"
        value={title}
        onChangeText={setTitle}
        disabled={uploading}
      />
      
      <Button
        title={uploading ? "Uploading & Analyzing..." : "Upload & Analyze"}
        onPress={handleUpload}
        disabled={!selectedMedia || uploading}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  preview: {
    width: '100%',
    height: 300,
    marginBottom: 20,
    borderRadius: 10,
  },
  placeholderContainer: {
    width: '100%',
    height: 300,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    borderRadius: 10,
  },
  placeholderText: {
    color: '#888',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ccc',
    marginBottom: 20,
    padding: 10,
    borderRadius: 5,
  },
});

export default UploadScreen;
```

## Error Handling

Create a consistent error handling approach:

```javascript
// app/utils/errorHandler.js
import { Alert } from 'react-native';

export const handleApiError = (error, context = 'Operation') => {
  console.error(`${context} error:`, error);
  
  // Extract error message
  let errorMessage = 'An unknown error occurred';
  
  if (error.response) {
    // Server responded with an error
    const data = error.response.data;
    
    if (typeof data === 'string') {
      errorMessage = data;
    } else if (data.detail) {
      errorMessage = data.detail;
    } else if (data.non_field_errors) {
      errorMessage = data.non_field_errors.join(', ');
    } else {
      // Try to find first error message
      const firstErrorKey = Object.keys(data)[0];
      if (firstErrorKey && data[firstErrorKey]) {
        const firstError = data[firstErrorKey];
        errorMessage = Array.isArray(firstError) 
          ? firstError.join(', ') 
          : String(firstError);
      }
    }
  } else if (error.message) {
    // Network error
    errorMessage = error.message;
  }
  
  // Show alert
  Alert.alert(
    `${context} Failed`,
    errorMessage,
    [{ text: 'OK' }]
  );
  
  return errorMessage;
};
```

## Connecting to Production

When deploying to production, update the API URL:

```javascript
// app/services/api.js
const API_URL = __DEV__ 
  ? 'http://localhost:8000/api'  // Development
  : 'https://api.protectedvision.com/api';  // Production
```

## Security Considerations

1. **Always validate all data** you send to the API
2. **Handle tokens securely** with AsyncStorage or SecureStore
3. **Use HTTPS** in production
4. **Never store sensitive information** in client-side code
5. **Implement proper logout** to clear tokens
6. **Add request timeouts** to handle network issues

## API Status Codes

- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid data submitted
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error 