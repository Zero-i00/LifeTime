'use client'

import { Controller, useForm } from 'react-hook-form'
import { valibotResolver } from '@hookform/resolvers/valibot'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Button, Input } from '@/shared/components/ui'
import { extractError } from '@/shared/api/api.error'
import { UserProfileUpdateSchema } from '../../schemas/user.schema'
import type { TypeUserProfileUpdate } from '../../types/user.types'
import { userQuery } from '../../queries/user.query'
import styles from './profile-form.module.css'

interface ProfileFormProps {
	defaultValues: TypeUserProfileUpdate
}

export function ProfileForm({ defaultValues }: ProfileFormProps) {
	const queryClient = useQueryClient()
	const { mutate, isPending } = useMutation(userQuery.updateProfile())

	const { control, handleSubmit } = useForm<TypeUserProfileUpdate>({
		mode: 'onChange',
		resolver: valibotResolver(UserProfileUpdateSchema),
		defaultValues,
	})

	const submit = (data: TypeUserProfileUpdate) => {
		mutate(data, {
			onSuccess: (updated) => {
				queryClient.setQueryData(userQuery.profile().queryKey, updated)
				toast.success('Профиль обновлён')
			},
			onError: (error) => {
				toast.error(extractError(error))
			},
		})
	}

	return (
		<form onSubmit={handleSubmit(submit)} className={styles.form}>
			<Controller
				name="full_name"
				control={control}
				render={({ field, fieldState }) => (
					<Input
						{...field}
						placeholder="Имя"
						error={fieldState.error?.message}
					/>
				)}
			/>

			<Controller
				name="email"
				control={control}
				render={({ field, fieldState }) => (
					<Input
						{...field}
						type="email"
						placeholder="Email"
						error={fieldState.error?.message}
					/>
				)}
			/>

			<div className={styles.actions}>
				<Button type="submit" isLoading={isPending}>
					Сохранить
				</Button>
			</div>
		</form>
	)
}
