// "use client";

// import React, { useState, useEffect, useCallback } from 'react';
// import { motion } from 'framer-motion';

// const Intralines = () => {
//   const [lines, setLines] = useState([]);
//   const [points, setPoints] = useState([]);
//   const [currentOrigin, setCurrentOrigin] = useState(null);
//   const [squares, setSquares] = useState([]);

//   const pointCount = 5;
//   const squareSize = 10;
//   const speed = 0.01;

//   // Função para gerar novos pontos aleatórios a partir de uma origem
//   const generatePoints = useCallback((origin) => {
//     const newPoints = [origin || randomPoint()];
//     for (let i = 1; i < pointCount; i++) {
//       newPoints.push(randomPoint());
//     }
//     setPoints(newPoints);
//     return newPoints;
//   }, []);

//   // Função para gerar um ponto aleatório no canvas
//   const randomPoint = () => {
//     return {
//       x: Math.random() * 400, // Canvas width
//       y: Math.random() * 380, // Canvas height
//     };
//   };

//   // Conectar pontos e gerar linhas
//   const connectPoints = useCallback((newPoints) => {
//     const newLines = [];
//     const newSquares = [];

//     // Conecte o ponto de origem a todos os outros
//     for (let i = 1; i < newPoints.length; i++) {
//       const pointA = newPoints[0];
//       const pointB = newPoints[i];

//       newLines.push({
//         startX: pointA.x,
//         startY: pointA.y,
//         endX: pointB.x,
//         endY: pointB.y,
//       });

//       // Criar quadrados que irão percorrer as linhas
//       newSquares.push({
//         startX: pointA.x,
//         startY: pointA.y,
//         endX: pointB.x,
//         endY: pointB.y,
//       });
//     }
//     setLines(newLines);
//     setSquares(newSquares);
//   }, []);

//   // Função que é chamada sempre que todos os quadrados terminam o trajeto
//   const generateNewStructure = useCallback(() => {
//     const origin = currentOrigin || randomPoint();
//     const newPoints = generatePoints(origin);
//     connectPoints(newPoints);
//     setCurrentOrigin(newPoints[Math.floor(Math.random() * newPoints.length)]); // Escolhe uma nova origem
//   }, [currentOrigin, connectPoints, generatePoints]);

//   // Gera a estrutura inicial
//   useEffect(() => {
//     generateNewStructure();
//   }, [generateNewStructure]);

//   return (
//     <div className="relative w-[400px] h-[380px] bg-transparent">
//       {lines.map((line, index) => (
//         <svg key={index} className="absolute top-0 left-0 w-full h-full">
//           <line
//             x1={line.startX}
//             y1={line.startY}
//             x2={line.endX}
//             y2={line.endY}
//             stroke="white"
//             strokeWidth="2"
//           />
//         </svg>
//       ))}

//       {squares.map((square, index) => {
//         const distance = Math.sqrt(
//           Math.pow(square.endX - square.startX, 2) + Math.pow(square.endY - square.startY, 2)
//         );

//         return (
//           <motion.div
//             key={index}
//             initial={{ x: square.startX, y: square.startY }}
//             animate={{ x: square.endX, y: square.endY }}
//             transition={{ duration: distance * speed, ease: 'linear' }}
//             className="absolute w-[10px] h-[10px] bg-white rounded-full"
//             onAnimationComplete={() => {
//               if (index === squares.length - 1) {
//                 generateNewStructure(); // Gera uma nova estrutura quando todos os quadrados terminam o trajeto
//               }
//             }}
//           />
//         );
//       })}
//     </div>
//   );
// };

// export default Intralines;
