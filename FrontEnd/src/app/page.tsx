'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/chat');
    } else {
      router.push('/auth/login');
    }
  }, [router]);

  return null; // This page will redirect immediately
}
