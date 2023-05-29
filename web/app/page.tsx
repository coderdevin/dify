import Link from 'next/link'
import Loading from '@/app/components/base/loading'
import { cookies } from 'next/headers'
import { useRouter } from 'next/navigation'

const Home = async () => {
  const cookieStore = cookies()
  const session = cookieStore.get('next-auth.session-token')
  if (!session) {
    const router = useRouter()
    router.push('www.smartcoder.ai/login')
    return
  }
  return (
    <div className="flex flex-col justify-center min-h-screen py-12 sm:px-6 lg:px-8">

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Loading type='area' />
        <div className="mt-10 text-center">
          <Link href='/apps'>🚀</Link>
        </div>
      </div>
    </div>
  )
}

export default Home
