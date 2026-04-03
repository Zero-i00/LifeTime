import ReactDiffViewer from "react-diff-viewer-continued";
import type { ILinkDiff } from "../types/diff.types";

export default function DiffView({ schema, different }: ILinkDiff) {
	return (
		<ReactDiffViewer oldValue={schema} newValue={different} splitView={true} />
	);
}
