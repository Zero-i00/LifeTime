import {
	dehydrate,
	HydrationBoundary,
	QueryClient,
} from "@tanstack/react-query";
import { LinkView } from "@/features/dashboard/link/views/links-views";

export default async function PlayerPage({
	params,
}: {
	params: Promise<{ id: string }>;
}) {
	const queryClient = new QueryClient();
	const { id } = await params;

	return (
		<HydrationBoundary state={dehydrate(queryClient)}>
			<LinkView id={id} />
		</HydrationBoundary>
	);
}
