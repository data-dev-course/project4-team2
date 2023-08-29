import React from 'react'
import ReactDOM from 'react-dom/client'
import Home from './components/Home.jsx'
import GrammarInfo from './components/GrammarInfo.jsx'
import App from './App.jsx'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import {
  QueryClient,
  QueryClientProvider
} from '@tanstack/react-query'
import GrammarDashboard from './components/GrammarDashboard.jsx'
import Ranking from './components/RankingChart.jsx'

const router = createBrowserRouter([
  {
    path: "/",
    element: <App/>,
    children: [
      { index: true, element: <Home /> },
      {
        path: "/data-info",
        element: <GrammarInfo/>
      },
      {
        path: "/dashboard",
        element: <GrammarDashboard/>
      },
      {
        path: "/ranking",
        element: <Ranking/>
      }
    ]
  },
]);

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}>
    <RouterProvider router={router} />
  </QueryClientProvider>
)
