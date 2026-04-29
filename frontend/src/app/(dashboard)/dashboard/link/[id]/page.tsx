import {
	dehydrate,
	HydrationBoundary,
	QueryClient,
} from "@tanstack/react-query";
import { LinkView } from "@/features/dashboard/link/views/links-views";
import { use } from 'react'
import { getQueryClient } from '@/app/providers/query-client'
import { linkQueries } from '@/features/dashboard/link/queries/link.queries'

interface Props {
	params: Promise<{ id: string }>
}

export default async function LinkPage({params}: Props) {
	const {id} = use(params)
	const queryClient = getQueryClient();

	await queryClient.prefetchQuery(linkQueries.retrieve(id))

	return (
		<HydrationBoundary state={dehydrate(queryClient)}>
			<LinkView id={id} />
		</HydrationBoundary>
	);
}
