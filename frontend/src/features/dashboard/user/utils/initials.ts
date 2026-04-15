export const getInitials = (fullName: string): string =>
	fullName
		.trim()
		.split(/\s+/)
		.slice(0, 2)
		.map(word => word[0]?.toUpperCase() ?? '')
		.join('')
