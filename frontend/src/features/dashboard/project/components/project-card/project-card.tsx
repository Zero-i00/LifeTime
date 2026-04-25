'use client'

import { useState } from 'react'
import { ChevronDown, Plus } from 'lucide-react'
import cn from 'clsx'
import { useQueryClient } from '@tanstack/react-query'
import styles from './project-card.module.css'
import { ProjectLinkItem } from '../project-link-item'
import type { TypeProjectResponse } from '../../types/project.types'

interface ProjectCardProps {
	project: TypeProjectResponse
}

export function ProjectCard({ project }: ProjectCardProps) {
	const [isOpen, setIsOpen] = useState(false)
	const [showForm, setShowForm] = useState(false)
	const [url, setUrl] = useState('')
	const queryClient = useQueryClient()
	const id = `project-links-${project.id}`

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		await fetch('/api/link/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ project_id: project.id, url })
		})
		await queryClient.invalidateQueries({ queryKey: ['projectQuery', 'list'] })
		setShowForm(false)
		setUrl('')
	}

	return (
		<li className={styles.card}>
			<button
				type="button"
				className={styles.header}
				onClick={() => setIsOpen(prev => !prev)}
				aria-expanded={isOpen}
				aria-controls={id}
			>
				<span className={styles.name}>{project.name}</span>
				<span className={styles.count}>{project.links.length} ссылок</span>
				<ChevronDown className={cn(styles.chevron, isOpen && styles['chevron--open'])} />
			</button>

			{isOpen && (
				<div id={id}>
					<button
						onClick={() => setShowForm(!showForm)}
						className={styles.addButton}
					>
						<Plus size={16} />
						Добавить ссылку
					</button>

					{showForm && (
						<form onSubmit={handleSubmit} className={styles.form}>
							<input
								type="url"
								value={url}
								onChange={(e) => setUrl(e.target.value)}
								placeholder="https://example.com"
								required
								className={styles.input}
							/>
							<button type="submit" className={styles.submitBtn}>
								Сохранить
							</button>
							<button
								type="button"
								onClick={() => setShowForm(false)}
								className={styles.cancelBtn}
							>
								Отмена
							</button>
						</form>
					)}

					{project.links.length > 0 ? (
						<ul className={styles.links}>
							{project.links.map(link => (
								<ProjectLinkItem key={link.id} link={link} />
							))}
						</ul>
					) : (
						<p className={styles.empty}>Нет ссылок</p>
					)}
				</div>
			)}
		</li>
	)
}
