'use client'
import { CssBaseline } from "@mui/material"
import Header from "./components/Header"
import { ReactQueryClientProvider } from "./components/ReactQueryProviders"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <ReactQueryClientProvider>
      <CssBaseline />
      
        <body>
        <Header/>
          {children}
        </body>
      </ReactQueryClientProvider>
    </html>
  )
}
