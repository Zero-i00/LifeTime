'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import cn from 'clsx'
import styles from './project-card.module.css'
import { ProjectLinkItem } from '../project-link-item'
import type { TypeProjectResponse } from '../../types/project.types'

interface ProjectCardProps {
	project: TypeProjectResponse
}

export function ProjectCard({ project }: ProjectCardProps) {
	const [isOpen, setIsOpen] = useState(false)
	const id = `project-links-${project.id}`

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
