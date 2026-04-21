import type { ReactNode } from 'react'
import { UserBadge } from '@/features/dashboard/user'
import { DASHBOARD_PAGE } from '@/shared/configs/page.config'
import { SidebarNavItem } from './sidebar-nav-item'
import styles from './sidebar.module.css'

interface SidebarProps {
	children?: ReactNode
}

export function Sidebar({ children }: SidebarProps) {
	return (
		<aside className={styles.sidebar}>
			<UserBadge />
			<nav className={styles.nav}>
				<SidebarNavItem href={DASHBOARD_PAGE.HOME} exact>
					Дашборд
				</SidebarNavItem>
				<SidebarNavItem href={DASHBOARD_PAGE.PROJECTS}>
					Проекты
				</SidebarNavItem>
			</nav>
			{children}
		</aside>
	)
}
