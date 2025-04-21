import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Message, Room, getMessages } from '@/lib/api';

interface UseChatProps {
  room: Room | null;
  onError?: (error: string) => void;
}

export function useChat({ room, onError }: UseChatProps) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 1000;

  const fetchOldMessages = async () => {
    if (!room) return;
    
    try {
      const response = await getMessages(room.id);
      if (response.success) {
        setMessages(response.data);
      } else {
        if (onError) onError('Failed to fetch messages');
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
      if (onError) onError('Error fetching messages');
    }
  };

  const connectToRoom = () => {
    if (!room) return;

    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
    }

    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      router.push('/auth/login');
      return;
    }

    // Get WebSocket URL from environment variable or use default
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002';
    const wsEndpoint = `${wsUrl}/ws/chat/${room.name}/?token=${encodeURIComponent(accessToken)}`;
    console.log('Connecting to WebSocket:', {
      wsUrl,
      roomName: room.name,
      token: accessToken ? 'present' : 'missing',
      endpoint: wsEndpoint
    });

    ws.current = new WebSocket(wsEndpoint);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      reconnectAttempts.current = 0;
      if (onError) onError('');
      // Fetch old messages when connected
      fetchOldMessages();
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        setMessages((prev) => [...prev, data]);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.current.onclose = (event) => {
      console.log('WebSocket disconnected with code:', event.code, 'reason:', event.reason);
      setIsConnected(false);

      // Handle specific close codes
      if (event.code === 1006) {
        // Abnormal closure - try to reconnect
        console.log('Attempting to reconnect...');
        reconnectAttempts.current++;
        if (reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(connectToRoom, reconnectDelay * reconnectAttempts.current);
        } else {
          if (onError) onError('Failed to connect to chat server');
        }
      } else if (event.code === 1008) {
        // Policy violation - token might be invalid
        console.error('Token might be invalid');
        router.push('/auth/login');
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError('WebSocket connection error');
    };
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || !room || !ws.current || ws.current.readyState !== WebSocket.OPEN) {
      if (onError) onError('Not connected to chat');
      return false;
    }

    try {
      const messageData = {
        type: 'chat_message',
        content,
        room: room.name
      };
      console.log('Sending message:', messageData);
      ws.current.send(JSON.stringify(messageData));
      setNewMessage('');
      if (onError) onError('');
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      if (onError) onError('Error sending message');
      return false;
    }
  };

  // Connect to room when room changes
  useEffect(() => {
    if (room) {
      connectToRoom();
    }
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [room]);

  return {
    messages,
    isConnected,
    newMessage,
    setNewMessage,
    sendMessage
  };
} 