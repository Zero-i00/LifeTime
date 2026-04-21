'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import cn from 'clsx'
import type { ReactNode } from 'react'
import styles from './sidebar.module.css'

interface SidebarNavItemProps {
	href: string
	children: ReactNode
	exact?: boolean
}

export function SidebarNavItem({ href, children, exact = false }: SidebarNavItemProps) {
	const pathname = usePathname()
	const isActive = exact ? pathname === href : pathname === href || pathname.startsWith(`${href}/`)

	return (
		<Link
			href={href}
			className={cn(styles['nav-item'], isActive && styles['nav-item--active'])}
		>
			{children}
		</Link>
	)
}
