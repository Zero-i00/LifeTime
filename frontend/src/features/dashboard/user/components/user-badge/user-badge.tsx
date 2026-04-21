'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Avatar } from '@/shared/components/ui'
import { DASHBOARD_PAGE } from '@/shared/configs/page.config'
import { userQuery } from '../../queries/user.query'
import { getInitials } from '../../utils/initials'
import styles from './user-badge.module.css'

export function UserBadge() {
	const { data, isPending } = useQuery(userQuery.profile())

	if (isPending) {
		return (
			<div className={styles.skeleton}>
				<div className={styles.skeleton__avatar} />
				<div className={styles.skeleton__lines}>
					<div className={`${styles.skeleton__line} ${styles['skeleton__line--name']}`} />
					<div className={`${styles.skeleton__line} ${styles['skeleton__line--email']}`} />
				</div>
			</div>
		)
	}

	if (!data) return null

	return (
		<Link href={DASHBOARD_PAGE.PROFILE} className={styles.root}>
			<Avatar initials={getInitials(data.full_name)} size="md" />
			<div className={styles.info}>
				<span className={styles.name}>{data.full_name}</span>
				<span className={styles.email}>{data.email}</span>
			</div>
		</Link>
	)
}
