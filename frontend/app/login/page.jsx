import Link from 'next/link'
import Image from 'next/image'

import { Button } from '@/components/ui/button'
import { Label } from '@radix-ui/react-dropdown-menu'
import { Input } from "@/components/ui/input"

const Login = () => {
  return (
    <div className="w-full lg:grid lg:min-h-[300px] lg:grid-cols-[2.2fr,2.5fr,0.5fr] xl:min-h-[500px] bg-accent-corfundo">
      <div className="flex items-center justify-center py-12">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="grid gap-2 mb-16 text-center lg:text-left">
            <h1 className="text-6xl text-cortexto ">LOGIN_</h1>
          </div>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="user" className="text-cortexto mb-6 text-2xl"><span className="text-red-800"> |</span>USER_</Label>
              <Input
                id="user"
                type="user"
                placeholder="User"
                required
                className="bg-transparent border-0 border-b-2 focus:outline-none rounded-none w-full text-white"
              />
              <p className="text-sm text-muted-foreground text-accent-textfd">nome do usuario</p>
            </div>
            <div className="grid gap-2">
              <div className="flex items-center mt-6">
                <Label htmlFor="password" className="text-cortexto mb-6 text-2xl"><span className="text-red-800"> |</span>PSWD_</Label>
              </div>
              <Input id="password" type="password" placeholder="*******" className="bg-transparent border-0 border-b-2 rounded-none focus:outline-none w-full" required />
              <p className="text-sm text-muted-foreground text-accent-textfd ">senha do usuario</p>
            </div>
            <Link href={'/home'}>
              <Button type="submit" variant="outline" className="w-full text-white bg-transparent hover:text-white">
                Login
              </Button>
            </Link>
          </div>
        </div>
      </div>
      <div className="hidden lg:flex justify-center items-center">
      <Image
        src="/Liner.png"
        alt="Image"
        width="400"
        height="380"
        className="object-cover" // provisório
      />
      </div>

      <div class="flex flex-col items-center">
        {/* <!-- Triângulos --> */}
          <div className="mt-10" >
          <div class="w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"></div>
          <div class="w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"></div>
          <div class="w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"></div>
          <div class="w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"></div>
          <div class="w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"></div>
          </div>
        {/* <!-- Linha vertical --> */}
        <div class="w-[2px] h-[350px] bg-white mt-2"></div>
      </div>
    </div>
  )
};

export default Login