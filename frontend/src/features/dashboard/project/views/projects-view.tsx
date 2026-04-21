'use client'

import { useQuery } from '@tanstack/react-query'
import { Loader } from '@/shared/components/ui'
import { projectQuery } from '../queries/project.query'
import { ProjectCard } from '../components/project-card'
import styles from './projects-view.module.css'

export function ProjectsView() {
	const { data, isPending } = useQuery(projectQuery.list())

	if (isPending) {
		return (
			<div className={styles.loader}>
				<Loader />
			</div>
		)
	}

	if (!data || data.length === 0) {
		return <p className={styles.empty}>У вас пока нет проектов</p>
	}

	return (
		<div className={styles.root}>
			<h1 className={styles.title}>Проекты</h1>
			<ul className={styles.list}>
				{data.map(project => (
					<ProjectCard key={project.id} project={project} />
				))}
			</ul>
		</div>
	)
}
