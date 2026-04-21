import styles from './avatar.module.css'
import cn from 'clsx'
import type { AvatarProps } from './avatar.types'

export function Avatar({ initials, size = 'md', className, 'aria-label': ariaLabel }: AvatarProps) {
	return (
		<span
			className={cn(styles.avatar, styles[`avatar--${size}`], className)}
			aria-label={ariaLabel ?? initials}
			role="img"
		>
			{initials}
		</span>
	)
}
