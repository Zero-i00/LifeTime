export type AvatarSize = 'sm' | 'md' | 'lg'

export interface AvatarProps {
	initials: string
	size?: AvatarSize
	className?: string
	'aria-label'?: string
}
