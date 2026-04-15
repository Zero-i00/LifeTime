import { queryOptions } from '@tanstack/react-query'
import { DASHBOARD_QUERY_KEY } from '@/shared/configs/query.config'
import { projectService } from '../services/project.service'

class ProjectQuery {
	public readonly BASE_KEY = [DASHBOARD_QUERY_KEY, 'project']

	list() {
		return queryOptions({
			queryKey: [...this.BASE_KEY, 'list'],
			queryFn: () => projectService.list(),
		})
	}
}

export const projectQuery = new ProjectQuery()
