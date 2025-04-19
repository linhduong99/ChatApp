'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getRooms, createRoom, Room } from '../lib/api';

export default function RoomList() {
  const router = useRouter();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomPassword, setNewRoomPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const response = await getRooms();
        if (response.success && Array.isArray(response.data)) {
          setRooms(response.data);
        } else {
          setRooms([]);
        }
      } catch (error) {
        console.error('Error fetching rooms:', error);
        setError('Failed to fetch rooms');
        setRooms([]);
      }
    };

    fetchRooms();
  }, []);

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoomName.trim()) return;

    try {
      const response = await createRoom({
        name: newRoomName,
        password: newRoomPassword || undefined,
      });

      if (response.success && response.data) {
        const newRoom = response.data;
        setRooms((prev) => [...prev, newRoom]);
        setNewRoomName('');
        setNewRoomPassword('');
      }
    } catch (error) {
      console.error('Error creating room:', error);
      setError('Failed to create room');
    }
  };

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chat Rooms</h1>
      
      {error && <div className="text-red-500 mb-4">{error}</div>}

      <form onSubmit={handleCreateRoom} className="mb-4">
        <div className="mb-2">
          <input
            type="text"
            value={newRoomName}
            onChange={(e) => setNewRoomName(e.target.value)}
            placeholder="Room name"
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-2">
          <input
            type="password"
            value={newRoomPassword}
            onChange={(e) => setNewRoomPassword(e.target.value)}
            placeholder="Password (optional)"
            className="w-full p-2 border rounded"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-500 text-white px-4 py-2 rounded"
        >
          Create Room
        </button>
      </form>

      <div className="space-y-2">
        {Array.isArray(rooms) && rooms.map((room) => (
          <div
            key={room.id}
            className="p-4 border rounded cursor-pointer hover:bg-gray-50"
            onClick={() => router.push(`/chat/${room.id}`)}
          >
            <div className="font-bold">{room.name}</div>
            <div className="text-sm text-gray-500">
              Created: {new Date(room.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 