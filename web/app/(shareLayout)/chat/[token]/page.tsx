'use client'
import type { FC } from 'react'
import React from 'react'
import { getCookie } from "cookies-next"
import type { IMainProps } from '@/app/components/share/chat'
import Main from '@/app/components/share/chat'
import { useRouter } from 'next/navigation'

const Chat: FC<IMainProps> = () => {
  const session = getCookie("__Secure-next-auth.session-token");
  if (!session) {
    const router = useRouter()
    router.push('https://www.smartcoder.ai/login')
  }
  return (
    <Main />
  )
}

export default React.memo(Chat)
