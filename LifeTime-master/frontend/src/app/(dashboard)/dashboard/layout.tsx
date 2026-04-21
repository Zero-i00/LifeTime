import type { ReactNode } from 'react'
import { Sidebar } from '@/shared/components/sidebar'
import styles from './layout.module.css'

interface DashboardLayoutProps {
	children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
	return (
		<div className={styles.layout}>
			<Sidebar />
			<main className={styles.main}>{children}</main>
		</div>
	)
}
