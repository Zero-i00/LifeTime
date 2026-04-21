'use client'

import { useQuery } from '@tanstack/react-query'
import { Loader } from '@/shared/components/ui'
import { userQuery } from '../queries/user.query'
import { ProfileForm } from '../components/profile-form'
import styles from './profile-view.module.css'

export function ProfileView() {
	const { data, isPending } = useQuery(userQuery.profile())

	if (isPending) {
		return (
			<div className={styles.loader}>
				<Loader />
			</div>
		)
	}

	if (!data) return null

	return (
		<div className={styles.root}>
			<h1 className={styles.title}>Профиль</h1>
			<div className={styles.card}>
				<ProfileForm defaultValues={{ full_name: data.full_name, email: data.email }} />
			</div>
		</div>
	)
}
