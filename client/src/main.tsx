import { configureApiClient } from '@/api/axios'
import { App } from '@/App'
import { AppRoutes } from '@/AppRoutes'
import { SessionProvider } from '@/auth/SessionProvider'
import '@/index.css'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router'

configureApiClient()

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
ReactDOM.createRoot(document.getElementById('root')!).render(
    <App>
        <SessionProvider>
            <BrowserRouter>
                <AppRoutes />
            </BrowserRouter>
        </SessionProvider>
    </App>
)
