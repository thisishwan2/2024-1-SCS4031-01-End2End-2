'use client'
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import Header from "./components/Header"


const queryClient = new QueryClient()

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <QueryClientProvider client={queryClient}>
      <Header/>
        <body>{children}</body>
      </QueryClientProvider>
    </html>
  )
}
