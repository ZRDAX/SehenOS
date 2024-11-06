"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Line } from "react-chartjs-2";
import { io } from "socket.io-client";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

import { CircleUser, Menu, Package2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";

const socket = io("http://localhost:4000");

export default function Dashboard() {
  const [packetData, setPacketData] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [packetFiles, setPacketFiles] = useState([]);
  const [anomalyFiles, setAnomalyFiles] = useState([]);
  const [packetTimes, setPacketTimes] = useState([]); 
  const [anomalyTimes, setAnomalyTimes] = useState([]); 
  const timePeriod = 15; // número de pontos de dados para exibir no gráfico

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const packetFilesRes = await fetch("/api/packet_backup");
        const anomalyFilesRes = await fetch("/api/anomaly_backup");

        if (!packetFilesRes.ok || !anomalyFilesRes.ok) {
          throw new Error("Falha ao buscar dados na API.");
        }

        const packetFilesData = await packetFilesRes.json();
        const anomalyFilesData = await anomalyFilesRes.json();

        setPacketFiles(packetFilesData);
        setAnomalyFiles(anomalyFilesData);
      } catch (error) {
        console.error("Erro ao buscar arquivos: ", error);
      }
    };

    fetchFiles();
  }, []);

  useEffect(() => {
    // configuração de dados em tempo real
    socket.on("packet_data", (data) => {
      const currentTime = new Date().toLocaleTimeString(); 
      setPacketData((prevData) => {
        const updatedData = [...prevData, data];
        return updatedData.length > timePeriod ? updatedData.slice(1) : updatedData;
      });
      setPacketTimes((prevTimes) => {
        const updatedTimes = [...prevTimes, currentTime];
        return updatedTimes.length > timePeriod ? updatedTimes.slice(1) : updatedTimes;
      });
    });

    socket.on("anomaly_data", (data) => {
      const currentTime = new Date().toLocaleTimeString();
      setAnomalyData((prevData) => {
        const updatedData = [...prevData, data];
        return updatedData.length > timePeriod ? updatedData.slice(1) : updatedData;
      });
      setAnomalyTimes((prevTimes) => {
        const updatedTimes = [...prevTimes, currentTime];
        return updatedTimes.length > timePeriod ? updatedTimes.slice(1) : updatedTimes;
      });
    });

    return () => {
      socket.off("packet_data");
      socket.off("anomaly_data");
    };
  }, []);

  const packetChartData = {
    labels: packetTimes,
    datasets: [
      {
        label: "Trafego de Rede",
        data: packetData,
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  };

  const anomalyChartData = {
    labels: anomalyTimes, 
    datasets: [
      {
        label: "Anomalias",
        data: anomalyData,
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="flex min-h-screen w-full flex-col bg-accent-corfundo text-white">
      <header className="sticky top-0 flex h-16 items-center gap-4 border-b bg-background px-4">
        <nav className="flex gap-6 text-lg font-medium">
          <Link href="#" className="font-semibold">
            Dashboard
          </Link>
          <Link href="#" className="text-muted-foreground transition-colors hover:text-foreground">
            Settings
          </Link>
        </nav>
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="outline"
              size="icon"
              className="shrink-0 md:hidden"
            >
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle navigation menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <nav className="grid gap-6 text-lg font-medium">
              <Link
                href="#"
                className="flex items-center gap-2 text-lg font-semibold"
              >
                <Package2 className="h-6 w-6" />
                <span className="sr-only">Acme Inc</span>
              </Link>
              <Link
                href="#"
                className="text-muted-foreground hover:text-foreground"
              >
                Dashboard
              </Link>
              <Link href="#" className="hover:text-foreground">
                Settings
              </Link>
            </nav>
          </SheetContent>
        </Sheet>
        <div className="flex w-full items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
          <form className="ml-auto flex-1 sm:flex-initial">
            <div className="relative">
            </div>
          </form>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="secondary" size="icon" className="rounded-full">
                <CircleUser className="h-5 w-5" />
                <span className="sr-only">Toggle user menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Support</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <main className="flex-1 p-4">
        <h1 className="text-3xl font-semibold mb-8">WIRES</h1>

        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <h2 className="text-2xl font-semibold mb-4">Trafego de Rede</h2>
            <Line data={packetChartData} />
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4">Anomalias</h2>
            <Line data={anomalyChartData} />
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">Arquivos de Backup</h2>
          <table className="w-full text-left border-separate border-spacing-2">
            <thead>
              <tr>
                <th className="px-4 py-2 border-b bg-gray-700">Tipo</th>
                <th className="px-4 py-2 border-b bg-gray-700">Nome do Arquivo</th>
              </tr>
            </thead>
            <tbody className="transition-all duration-300 ease-in-out">
              {packetFiles.map((file, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-gray-800 transition-all duration-300"
                >
                  <td className="px-4 py-2 border-b">{`Capture`}</td>
                  <td className="px-4 py-2 border-b">{file}</td>
                </tr>
              ))}
              {anomalyFiles.map((file, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-gray-800 transition-all duration-300"
                >
                  <td className="px-4 py-2 border-b">{`Anomalie`}</td>
                  <td className="px-4 py-2 border-b">{file}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>

      <style jsx>{`
        .text-muted-foreground {
          color: #9a9a9a;
        }
        .text-foreground:hover {
          color: #fff;
        }
        table {
          border-collapse: separate;
          border-spacing: 0;
        }
        tbody tr:hover {
          background-color: #2d2d2d;
        }
        th {
          text-align: left;
          padding: 8px;
          background-color: #333;
          color: white;
        }
        td {
          padding: 8px;
          border-bottom: 1px solid #444;
        }
      `}</style>
    </div>
  );
}
