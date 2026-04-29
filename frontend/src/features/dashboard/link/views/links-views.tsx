import { useSuspenseQuery } from "@tanstack/react-query";
import ReactDiffViewer from "react-diff-viewer-continued";
import { linkQueries } from "../queries/link.queries";

export function LinkView({ id }: { id: string }) {
	const { data } = useSuspenseQuery(linkQueries.retrieve(id));

	// TODO view all info
	return (
		<ReactDiffViewer
			oldValue={data.schema}
			newValue={data.different}
			splitView={true}
		/>
	);
}
