"use client";

import Header from "@/components/ui/header";
import Footer from "@/components/ui/footer";
import { useState, useEffect } from "react";
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
  Legend,
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

const socket = io("http://localhost:4000");

export default function Dashboard() {
  const [packetData, setPacketData] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [packetFiles, setPacketFiles] = useState([]);
  const [anomalyFiles, setAnomalyFiles] = useState([]);
  const [packetTimes, setPacketTimes] = useState([]);
  const [anomalyTimes, setAnomalyTimes] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [systemSummary, setSystemSummary] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [packetFilesRes, anomalyFilesRes] = await Promise.all([
          fetch("http://192.168.1.115:5000/api/packet_backup"),
          fetch("http://192.168.1.115:5000/api/anomaly_backup"),
        ]);

        setPacketFiles(await packetFilesRes.json());
        setAnomalyFiles(await anomalyFilesRes.json());

        const [packetsRes, anomaliesRes] = await Promise.all([
          fetch("http://192.168.1.115:5000/api/packets"),
          fetch("http://192.168.1.115:5000/api/anomalies"),
        ]);

        const packetsData = await packetsRes.json();
        const anomaliesData = await anomaliesRes.json();

        setPacketData(packetsData.map((p) => p.value));
        setAnomalyData(anomaliesData.map((a) => a.value));
        setPacketTimes(packetsData.map((p) => p.timestamp));
        setAnomalyTimes(anomaliesData.map((a) => a.timestamp));

        const [systemInfoRes, systemSummaryRes] = await Promise.all([
          fetch("http://192.168.1.115:5000/api/system_info"),
          fetch("http://192.168.1.115:5000/api/system_summary"),
        ]);

        setSystemInfo(await systemInfoRes.json());
        setSystemSummary(await systemSummaryRes.json());
      } catch (error) {
        console.error("Erro ao buscar dados: ", error);
      }
    };

    fetchData();
  }, []);

  const packetChartData = {
    labels: packetTimes,
    datasets: [
      {
        label: "Tráfego de Rede",
        data: packetData,
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 2,
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
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-accent-corfundo to-black text-white">
      <Header />

      <main className="container mx-auto px-4 py-12">
        <h1 className="text-4xl lg:text-5xl font-bold text-center text-cortexto mb-12">
          WIRES
        </h1>

        {/* Gráficos */}
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="bg-accent-corfundo p-6 rounded-lg shadow-lg overflow-x-auto">
            <h2 className="text-2xl font-semibold mb-4 text-cortexto">Tráfego de Rede</h2>
            <div className="relative h-64 w-full">
              <Line data={packetChartData} options={chartOptions} />
            </div>
          </div>

          <div className="bg-accent-corfundo p-6 rounded-lg shadow-lg overflow-x-auto">
            <h2 className="text-2xl font-semibold mb-4 text-cortexto">Anomalias</h2>
            <div className="relative h-64 w-full">
              <Line data={anomalyChartData} options={chartOptions} />
            </div>
          </div>
        </div>

        {/* Backups */}
        <div className="mt-12 bg-black p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold text-cortexto mb-4">Arquivos de Backup</h2>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="px-4 py-2 border-b text-cortexto">Tipo</th>
                <th className="px-4 py-2 border-b text-cortexto">Nome do Arquivo</th>
              </tr>
            </thead>
            <tbody>
              {packetFiles.map((file, idx) => (
                <tr key={idx} className="hover:bg-accent-corfundo">
                  <td className="px-4 py-2 border-b">Captura</td>
                  <td className="px-4 py-2 border-b">{file}</td>
                </tr>
              ))}
              {anomalyFiles.map((file, idx) => (
                <tr key={idx} className="hover:bg-accent-corfundo">
                  <td className="px-4 py-2 border-b">Anomalia</td>
                  <td className="px-4 py-2 border-b">{file}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Informações do Sistema */}
        <div className="grid gap-8 md:grid-cols-2 mt-12">
          <div className="bg-accent-corfundo p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold text-cortexto mb-4">Informações do Sistema</h2>
            {systemInfo ? (
              <pre className="text-sm bg-black p-4 rounded-lg">{JSON.stringify(systemInfo, null, 2)}</pre>
            ) : (
              <p>Carregando...</p>
            )}
          </div>

          <div className="bg-accent-corfundo p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold text-cortexto mb-4">Resumo de Informações</h2>
            {systemSummary ? (
              <pre className="text-sm bg-black p-4 rounded-lg">{JSON.stringify(systemSummary, null, 2)}</pre>
            ) : (
              <p>Carregando...</p>
            )}
          </div>
        </div>
      </main>

      <Footer />
      
    </div>
  );
}
