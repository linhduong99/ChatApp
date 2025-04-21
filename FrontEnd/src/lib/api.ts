// Types
export interface User {
  id: number;
  username: string;
  email?: string;
  avatar?: string;
}

export interface Room {
  id: number;
  name: string;
  created_at: string;
  has_password?: boolean;
}

export interface Message {
  id: number;
  content: string;
  user: User;
  room: number;
  created_at: string;
}

// API base URL
const API_BASE_URL = 'http://localhost:8002/api';

// Helper function for API calls
async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<{ success: boolean; data: T }> {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  
  // Don't try to refresh token for login, register, or token refresh endpoints
  const isAuthEndpoint = endpoint === '/users/login/' || 
                         endpoint === '/users/' || 
                         endpoint === '/token/refresh/';
  
  // Log the request details for debugging
  console.log('API Request:', {
    endpoint,
    hasAccessToken: !!accessToken,
    hasRefreshToken: !!refreshToken,
    isAuthEndpoint
  });

  const headers = {
    'Content-Type': 'application/json',
    ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
    ...options.headers,
  };

  // Log the headers being sent
  console.log('Request headers:', headers);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers,
  });

  // Log the response status
  console.log('API Response status:', response.status);

  // Only try to refresh token if it's not an auth endpoint and we have a refresh token
  if (response.status === 401 && !isAuthEndpoint && refreshToken) {
    console.log('Attempting token refresh...');
    try {
      // Try to refresh the token
      const refreshResponse = await fetch(`${API_BASE_URL}/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      console.log('Token refresh response status:', refreshResponse.status);

      if (refreshResponse.ok) {
        const { access } = await refreshResponse.json();
        localStorage.setItem('access_token', access);
        
        // Retry the original request with new token
        const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${access}`,
            ...options.headers,
          },
        });
        
        console.log('Retry response status:', retryResponse.status);
        
        if (!retryResponse.ok) {
          throw new Error(`API error: ${retryResponse.status}`);
        }
        
        const data = await retryResponse.json();
        return { success: true, data };
      } else {
        // If refresh fails, clear tokens and redirect to login
        console.log('Token refresh failed, clearing tokens...');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // window.location.href = '/auth/login';
        throw new Error('Session expired');
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    //   window.location.href = '/auth/login';
      throw new Error('Session expired');
    }
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = await response.json();
  return { success: true, data };
}

// Room API functions
export async function getRooms(): Promise<{ success: boolean; data: Room[] }> {
  return fetchAPI<Room[]>('/rooms/');
}

export async function getRoom(id: number): Promise<{ success: boolean; data: Room }> {
  return fetchAPI<Room>(`/rooms/${id}/`);
}

export async function createRoom(name: string, password?: string): Promise<{ success: boolean; data: Room }> {
  return fetchAPI<Room>('/rooms/', {
    method: 'POST',
    body: JSON.stringify({ name, password }),
  });
}

export async function verifyRoomPassword(roomId: number, password: string): Promise<{ success: boolean; data: boolean }> {
  return fetchAPI<boolean>(`/rooms/${roomId}/verify-password/`, {
    method: 'POST',
    body: JSON.stringify({ password }),
  });
}

// Message API functions
export async function getMessages(roomId: number): Promise<{ success: boolean; data: Message[] }> {
  try {
    return await fetchAPI<Message[]>(`/messages/?room_id=${roomId}`);
  } catch (error) {
    console.error('Error fetching messages:', error);
    return { success: false, data: [] };
  }
}

export async function sendMessage(roomId: number, content: string): Promise<{ success: boolean; data: Message }> {
  return fetchAPI<Message>(`/rooms/${roomId}/messages/`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

// User API functions
export async function getCurrentUser(): Promise<{ success: boolean; data: User }> {
  try {
    return await fetchAPI<User>('/users/me/');
  } catch (error) {
    return { success: false, data: null as any };
  }
}

export async function login(username: string, password: string): Promise<{ success: boolean; data: { user: User; tokens: { access: string; refresh: string } } }> {
  try {
    const response = await fetchAPI<{ user: User; tokens: { access: string; refresh: string } }>('/users/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    // Log the login response
    console.log('Login response:', {
      success: response.success,
      user: response.data?.user,
      hasAccessToken: !!response.data?.tokens?.access,
      hasRefreshToken: !!response.data?.tokens?.refresh
    });

    if (response.success) {
      localStorage.setItem('access_token', response.data.tokens.access);
      localStorage.setItem('refresh_token', response.data.tokens.refresh);
    }

    return response;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

export async function register(username: string, password: string): Promise<{ success: boolean; data: { user: User; tokens: { access: string; refresh: string } } }> {
  const response = await fetchAPI<{ user: User; tokens: { access: string; refresh: string } }>('/users/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });

  if (response.success) {
    localStorage.setItem('access_token', response.data.tokens.access);
    localStorage.setItem('refresh_token', response.data.tokens.refresh);
  }

  return response;
}

export async function logout(): Promise<{ success: boolean }> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    try {
      await fetchAPI('/users/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh: refreshToken }),
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  return { success: true };
} 