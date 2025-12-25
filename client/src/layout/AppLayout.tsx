import { Outlet } from 'react-router'

export function AppLayout() {
    return (
        <div>
            <header>Header</header>
            <Outlet />
        </div>
    )
}
