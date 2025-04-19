'use client';

import Chat from '@/components/Chat';

interface ChatPageProps {
  params: {
    roomId: string;
  };
}

export default function ChatPage({ params }: ChatPageProps) {
  return (
    <div className="h-full">
      <Chat roomId={params.roomId} />
    </div>
  );
} 