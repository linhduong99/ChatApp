'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getRoom } from '@/lib/api';

interface RoomPageProps {
  params: {
    id: string;
  };
}

export default function RoomPage({ params }: RoomPageProps) {
  const { id } = params;
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRoom = async () => {
      if (!isLoading) return;
      
      try {
        const response = await getRoom(Number(id));
        if (response.success) {
          router.push(`/chat?room=${response.data.id}`);
        } else {
          router.push('/chat');
        }
      } catch (error) {
        console.error('Error fetching room:', error);
        router.push('/chat');
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchRoom();
    }
  }, [id, router, isLoading]);

  return null;
} 