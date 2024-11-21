"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Image from "next/image";

const Login = () => {
  const [step, setStep] = useState(0);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [wireName, setWireName] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");

  const steps = [
    {
      title: "LOGIN",
      fields: [
        { placeholder: "Seu email", type: "email", value: email, setValue: setEmail },
        { placeholder: "Crie uma senha", type: "password", value: password, setValue: setPassword },
      ],
    },
    {
      title: "INFORMAÇÕES PESSOAIS",
      fields: [
        { placeholder: "Nome completo", type: "text", value: fullName, setValue: setFullName },
        { placeholder: "Nome de usuário", type: "text", value: username, setValue: setUsername },
      ],
    },
    {
      title: "PERSONALIZE SEU WIRE",
      fields: [
        { placeholder: "Nome do Wire", type: "text", value: wireName, setValue: setWireName },
        { placeholder: "Descrição", type: "text", value: description, setValue: setDescription },
        { placeholder: "Local", type: "text", value: location, setValue: setLocation },
      ],
    },
  ];

  const handleNextStep = () => {
    if (step < steps.length - 1) setStep(step + 1);
  };

  const handlePreviousStep = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleFormSubmit = () => {
    const formData = {
      email,
      password,
      fullName,
      username,
      wireName,
      description,
      location,
    };

    console.log("Dados do formulário:", formData);
    //Alterar para fazer envio dos dados

  };

  return (
    <div className="w-full min-h-screen md:grid md:grid-cols-[2.2fr,2.5fr,0.5fr] bg-accent-corfundo relative overflow-hidden">
      <div className="flex items-center justify-center py-12 transition-all duration-500">
        <div className="mx-auto grid w-[350px] gap-6 mt-12 align-middle">
          <div className="ml-6 mr-6">
            <div className="grid gap-2 mb-16 text-center md:text-left">
              <h1 className="text-4xl md:text-6xl text-cortexto">
                {steps[step].title}
              </h1>
            </div>
            <div className="grid gap-4">
              {steps[step].fields.map((field, index) => (
                <div key={index}>
                  <Input
                    type={field.type}
                    placeholder={field.placeholder}
                    value={field.value}
                    onChange={(e) => field.setValue(e.target.value)}
                    required
                    className="bg-transparent border-0 border-b-2 focus:outline-none rounded-none w-full text-white"
                  />
                </div>
              ))}
              <div className="flex justify-between mt-4">
                {step > 0 && (
                  <Button
                    onClick={handlePreviousStep}
                    className="text-white bg-transparent hover:text-red-800"
                  >
                    VOLTAR
                  </Button>
                )}
                {step < steps.length - 1 ? (
                  <Button
                    onClick={handleNextStep}
                    className="text-white bg-transparent hover:text-red-800"
                  >
                    CONTINUAR
                  </Button>
                ) : (
                  <Link href="/dashboard">
                    <Button
                      onClick={handleFormSubmit}
                      className="text-white bg-transparent hover:text-red-800"
                    >
                      FINALIZAR
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Linha e triângulos */}
      <div className="hidden md:flex flex-col items-center absolute right-6 inset-y-0 justify-center">
        <div className="relative h-[60%] w-[2px] bg-white">
          {steps.map((stepData, index) => (
            <div
              key={index}
              className="flex items-center absolute left-1/2 transform -translate-x-1/2"
              style={{
                top: `${(index + 1) * (100 / (steps.length + 1))}%`,
                transform: "translate(-50%, -50%)",
              }}
            >
              <span
                className="text-white text-sm lg:text-base absolute right-[130%] text-right whitespace-nowrap mr-4"
              >
                {stepData.title}
              </span>
              <div
                className={`transition-all duration-500 ${step === index
                  ? "rotate-180 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"
                  : step > index
                    ? "border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-white"
                    : "border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-b-[20px] border-b-red-500"
                  }`}
              ></div>
            </div>
          ))}
        </div>
      </div>

      <div className="w-full ml-12 hidden xl:flex justify-left items-center">
        <Image
          src="/Liner.png"
          alt="Image"
          width={380}
          height={380}
          className="object-cover"
        />
      </div>
    </div>

  );
};

export default Login;
