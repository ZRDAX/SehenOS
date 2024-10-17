import Link from "next/link";
import { Button } from "@/components/ui/button";
export function Home() {
  return (<div>
    <Link href={'/login'}>
      <Button type="submit" className="w-full bg-black hover:bg-gray-950">
        Login
      </Button>
    </Link>
  </div>
  )
};

export default Home;