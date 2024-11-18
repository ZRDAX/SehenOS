"use client";

import Header from "@/components/ui/header";
import Footer from "@/components/ui/footer";
import Image from "next/image";
import Link from "next/link";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-accent-corfundo text-white relative">
      <Header />

      {/* Hero Section */}
      <section className="w-full py-20 text-center bg-gradient-to-b from-accent-corfundo to-black">
        <div className="container mx-auto px-6 flex flex-col md:flex-row items-center">
          <div className="flex-1 mb-10 md:mb-0 text-center md:text-left">
            <h1 className="text-4xl lg:text-6xl font-bold mb-6 text-cortexto">
              Segurança e Acessibilidade em um Só Lugar
            </h1>
            <div className="flex justify-center md:hidden mb-6">
              <Image
                src="/logosehen-removebg-preview.png"
                alt="Image"
                width={300}
                height={300}
                className="object-contain"
              />
            </div>
            <p className="text-lg lg:text-2xl text-gray-300 mb-6">
              Um sistema focado em análise e cibersegurança para redes, acessível e poderoso.
            </p>
            <Link href="/login">
              <button className="mt-4 px-6 py-3 bg-red-800 hover:bg-red-600 text-white rounded-md transition-all">
                Saiba Mais
              </button>
            </Link>
          </div>
          <div className="hidden md:flex justify-center w-full md:w-auto">
            <Image
              src="/logosehen.png"
              alt="Image"
              width={400}
              height={400}
              className="object-contain"
            />
          </div>
        </div>
      </section>

      {/* Funcionalidades */}
      <section id="features" className="py-20 bg-black text-white">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold mb-8 text-center text-red-800 break-words px-4">
            Funcionalidades Principais
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="p-6 bg-accent-corfundo rounded-lg shadow-md hover:scale-105 transition-all">
              <h3 className="text-xl font-semibold text-cortexto">Monitoramento Contínuo</h3>
              <p className="mt-4 text-gray-300">
                Inspeção de pacotes em tempo real com técnicas avançadas de port mirroring.
              </p>
            </div>
            <div className="p-6 bg-accent-corfundo rounded-lg shadow-md hover:scale-105 transition-all">
              <h3 className="text-xl font-semibold text-cortexto">Detecção de Ameaças</h3>
              <p className="mt-4 text-gray-300">
                Identifique padrões de comportamento com Machine Learning e análise de dados.
              </p>
            </div>
            <div className="p-6 bg-accent-corfundo rounded-lg shadow-md hover:scale-105 transition-all">
              <h3 className="text-xl font-semibold text-cortexto">Interface Intuitiva</h3>
              <p className="mt-4 text-gray-300">
                Acesse dados de forma clara e simples, mesmo sem conhecimento técnico avançado.
              </p>
            </div>
            <div className="p-6 bg-accent-corfundo rounded-lg shadow-md hover:scale-105 transition-all">
              <h3 className="text-xl font-semibold text-cortexto">Relatórios Detalhados</h3>
              <p className="mt-4 text-gray-300">
                Gere relatórios personalizáveis para análise detalhada das redes monitoradas.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Tecnologia */}
      <section id="technology" className="py-20 bg-gradient-to-t from-black to-accent-corfundo">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-red-800 mb-8">Tecnologia Avançada</h2>
          <p className="text-gray-300 lg:w-2/3 mx-auto">
            Baseado em Linux, o sistema aproveita o poder do open-source para oferecer flexibilidade,
            segurança e desempenho. Feito para dispositivos SBC, garantindo economia e eficiência.
          </p>
          <Image
            src="/"
            alt=""
            width={600}
            height={400}
            className="mt-8 mx-auto"
          />
        </div>
      </section>

      {/* Contato */}
      <section id="contact" className="py-20 bg-black text-white">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold mb-8 text-center text-red-800">
            Fale Conosco
          </h2>
          <div className="max-w-lg mx-auto">
            <form className="space-y-6">
              <input
                type="text"
                placeholder="Seu Nome"
                className="w-full p-3 rounded bg-accent-corfundo text-white focus:outline-none"
              />
              <input
                type="email"
                placeholder="Seu Email"
                className="w-full p-3 rounded bg-accent-corfundo text-white focus:outline-none"
              />
              <textarea
                rows="4"
                placeholder="Sua Mensagem"
                className="w-full p-3 rounded bg-accent-corfundo text-white focus:outline-none"
              ></textarea>
              <button
                type="submit"
                className="w-full bg-red-800 hover:bg-red-600 py-3 rounded text-white font-semibold transition-all"
              >
                Enviar Mensagem
              </button>
            </form>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingPage;
