"use client";

import { AiOutlinePoweroff, AiOutlineReload } from "react-icons/ai";
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

const API_BASE = "http://10.0.3.230:5000";

export default function Dashboard() {
  const [packetData, setPacketData] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [packetFiles, setPacketFiles] = useState([]);
  const [anomalyFiles, setAnomalyFiles] = useState([]);
  const [packetTimes, setPacketTimes] = useState([]);
  const [anomalyTimes, setAnomalyTimes] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [systemSummary, setSystemSummary] = useState(null);
  const [blacklist] = useState([]);
  const [whitelist] = useState([]);

  useEffect(() => {
    const socket = io({ API_BASE });
    socket.on("packets", (newPacket) => {
      setPacketData((prevData) => [...prevData, newPacket.value]);
      setPacketTimes((prevTimes) => [...prevTimes, newPacket.timestamp]);
    });

    socket.on("anomalies", (newAnomaly) => {
      setAnomalyData((prevData) => [...prevData, newAnomaly.value]);
      setAnomalyTimes((prevTimes) => [...prevTimes, newAnomaly.timestamp]);
    });

    const fetchData = async () => {
      try {
        const [packetFilesRes, anomalyFilesRes] = await Promise.all([
          fetch("{API_BASE}/api/list_packet_backup"),
          fetch("{API_BASE}/api/anomaly_backup"),
        ]);

        const packetFilesData = await packetFilesRes.json();
        const anomalyFilesData = await anomalyFilesRes.json();

        setPacketFiles(Array.isArray(packetFilesData) ? packetFilesData : []);
        setAnomalyFiles(Array.isArray(anomalyFilesData) ? anomalyFilesData : []);

        const [packetsRes, anomaliesRes] = await Promise.all([
          fetch("{API_BASE}/api/packets"),
          fetch("{API_BASE}/api/anomalies"),
        ]);

        const packetsData = await packetsRes.json();
        const anomaliesData = await anomaliesRes.json();

        setPacketData(packetsData.map((p) => p.value));
        setAnomalyData(anomaliesData.map((a) => a.value));
        setPacketTimes(packetsData.map((p) => p.timestamp));
        setAnomalyTimes(anomaliesData.map((a) => a.timestamp));

        const [systemInfoRes, systemSummaryRes] = await Promise.all([
          fetch("{API_BASE}/api/system_info"),
          fetch("{API_BASE}/api/system_summary"),
        ]);

        setSystemInfo(await systemInfoRes.json());
        setSystemSummary(await systemSummaryRes.json());
      } catch (error) {
        console.error("Erro ao buscar dados: ", error);
      }
    };

    fetchData();

    return () => {
      socket.disconnect();
    };
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

  const handleReboot = async () => {
    try {
      await fetch(`${API_BASE}/reboot_sys`, { method: "POST" });
      alert("Reiniciando o dispositivo...");
    } catch (error) {
      console.error("Erro ao reiniciar o dispositivo:", error);
    }
  };

  const handleShutdown = async () => {
    try {
      await fetch(`${API_BASE}/shutdown_sys`, { method: "POST" });
      alert("Desligando o dispositivo...");
    } catch (error) {
      console.error("Erro ao desligar o dispositivo:", error);
    }
  };

  const saveBackup = async (endpoint) => {
    try {
      await fetch(`${API_BASE}/${endpoint}`, { method: "POST" });
      alert(`Backup salvo com sucesso: ${endpoint}`);
    } catch (error) {
      console.error(`Erro ao salvar backup (${endpoint}):`, error);
      alert(`Erro ao salvar backup (${endpoint}).`);
    }
  };

  const addToList = async (endpoint, ip) => {
    try {
      await fetch(`${API_BASE}/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip }),
      });
      alert(`IP ${ip} adicionado com sucesso!`);
    } catch (error) {
      console.error(`Erro ao adicionar IP (${ip}) em ${endpoint}:`, error);
      alert(`Erro ao adicionar IP.`);
    }
  };

  const removeFromList = async (endpoint, ip) => {
    try {
      await fetch(`${API_BASE}/${endpoint}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip }),
      });
      alert(`IP ${ip} removido com sucesso!`);
    } catch (error) {
      console.error(`Erro ao remover IP (${ip}) de ${endpoint}:`, error);
      alert(`Erro ao remover IP.`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-accent-corfundo to-black text-white">

      <main className="container mx-auto px-4 py-12">
        <h1 className="text-4xl lg:text-5xl font-bold text-center text-cortexto mb-12 mt-12">
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
              {(packetFiles || []).map((file, idx) => (
                <tr key={idx} className="hover:bg-accent-corfundo">
                  <td className="px-4 py-2 border-b">Captura</td>
                  <td className="px-4 py-2 border-b">{file}</td>
                </tr>
              ))}
              {(anomalyFiles || []).map((file, idx) => (
                <tr key={idx} className="hover:bg-accent-corfundo">
                  <td className="px-4 py-2 border-b">Anomalia</td>
                  <td className="px-4 py-2 border-b">{file}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>


        {/* Salvar Backups */}
        <div className="flex gap-4 mt-4">
          <button
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition"
            onClick={() => saveBackup("save_packet_backup")}
          >
            Salvar Backup de Pacotes
          </button>
          <button
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition"
            onClick={() => saveBackup("save_anomaly_backup")}
          >
            Salvar Backup de Anomalias
          </button>
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

        {/* Blacklist e Whitelist */}
        <div className="mt-8">
          <h2 className="text-2xl font-semibold text-cortexto mb-4">Blacklist</h2>
          <div className="flex gap-2 mb-4">
            <input
              id="blacklist-ip"
              type="text"
              placeholder="Digite o IP"
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none text-black"
              pattern="^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$"
            />
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
              onClick={() => {
                const ip = document.querySelector("#blacklist-ip").value;
                addToList("blacklist_edit", ip);
              }}
            >
              Adicionar
            </button>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="px-4 py-2 border-b text-cortexto">Endereço IP</th>
                <th className="px-4 py-2 border-b text-cortexto">Ações</th>
              </tr>
            </thead>
            <tbody>
              {blacklist.map((ip, idx) => (
                <tr key={idx} className="hover:bg-accent-corfundo">
                  <td className="px-4 py-2 border-b">{ip}</td>
                  <td className="px-4 py-2 border-b">
                    <button
                      className="text-red-600 hover:text-red-800"
                      onClick={() => removeFromList("blacklist_edit", ip)}
                    >
                      ❌
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>


          <div className="mt-8">
            <h2 className="text-2xl font-semibold text-cortexto mb-4">Whitelist</h2>
            <div className="flex gap-2 mb-4">
              <input
                id="whitelist-ip"
                type="text"
                placeholder="Digite o IP"
                className="flex-1 px-4 py-2 border rounded-lg focus:outline-none text-black"
                pattern="^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$"
              />
              <button
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
                onClick={() => {
                  const ip = document.querySelector("#whitelist-ip").value;
                  addToList("whitelist_edit", ip);
                }}
              >
                Adicionar
              </button>
            </div>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr>
                  <th className="px-4 py-2 border-b text-cortexto">Endereço IP</th>
                  <th className="px-4 py-2 border-b text-cortexto">Ações</th>
                </tr>
              </thead>
              <tbody>
                {whitelist.map((ip, idx) => (
                  <tr key={idx} className="hover:bg-accent-corfundo">
                    <td className="px-4 py-2 border-b">{ip}</td>
                    <td className="px-4 py-2 border-b">
                      <button
                        className="text-red-600 hover:text-red-800"
                        onClick={() => removeFromList("whitelist_edit", ip)}
                      >
                        ❌
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Botões de Reiniciar e Desligar */}
        <div className="grid gap-4 grid-cols-2 mt-8">
          <button
            onClick={handleReboot}
            className="flex items-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-4 rounded-full transition-transform hover:scale-105"
          >
            <AiOutlineReload className="text-2xl" />
            Reiniciar Dispositivo
          </button>
          <button
            onClick={handleShutdown}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-full transition-transform hover:scale-105"
          >
            <AiOutlinePoweroff className="text-2xl" />
            Desligar Dispositivo
          </button>
        </div>
      </main>
    </div>
  );
}
