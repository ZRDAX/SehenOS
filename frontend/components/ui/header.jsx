"use client";

import Link from "next/link";
import Image from "next/image";

const Header = () => {
  return (
    <header className="w-full bg-accent-corfundo text-white py-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center px-6">
      <div className="hiddenlg:flex justify-center items-center">
        <Image
          src="/logosehen.png"
          alt="SehenWire logo"
          width={60}
          height={60}
          className="object-cover"
        />
      </div>
        <nav className="flex space-x-6">
          <Link href="#features">Funcionalidades</Link>
          <Link href="#technology">Tecnologia</Link>
          <Link href="#contact">Contato</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
