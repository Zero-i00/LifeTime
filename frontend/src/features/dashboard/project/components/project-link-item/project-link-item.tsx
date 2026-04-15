import styles from './project-link-item.module.css'
import cn from 'clsx'
import type { TypeLinkResponse } from '../../types/project.types'

interface ProjectLinkItemProps {
	link: TypeLinkResponse
}

export function ProjectLinkItem({ link }: ProjectLinkItemProps) {
	const change = link.change_percentage

	return (
		<li className={styles.item}>
			<a
				href={link.url}
				target="_blank"
				rel="noopener noreferrer"
				className={styles.url}
				title={link.url}
			>
				{link.url}
			</a>
			<div className={styles.meta}>
				{link.tag && <span className={styles.tag}>{link.tag}</span>}
				{change !== null && change !== undefined && (
					<span className={cn(styles.change, change < 0 && styles['change--negative'])}>
						{change > 0 ? '+' : ''}{change.toFixed(1)}%
					</span>
				)}
			</div>
		</li>
	)
}
