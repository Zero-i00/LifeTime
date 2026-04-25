import { useQuery } from "@tanstack/react-query";
import ReactDiffViewer from "react-diff-viewer-continued";
import { linkQueries } from "../queries/link.queries";

export function LinkView({ id }: { id: string }) {
	const { data } = useQuery(linkQueries.retrieve(id));

	if (!data) return null;

	return (
		<ReactDiffViewer
			oldValue={data.schema}
			newValue={data.different}
			splitView={true}
		/>
	);
}
