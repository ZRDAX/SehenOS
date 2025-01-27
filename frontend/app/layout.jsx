import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const jetBrainsMono = JetBrains_Mono({ subsets: ["latin"] });

export const metadata = {
  title: "SehenWire",
  description: "Sehen Wire Website",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-br">
      <body className={jetBrainsMono.className}>
        {children}
        </body>
    </html>
  );
}
