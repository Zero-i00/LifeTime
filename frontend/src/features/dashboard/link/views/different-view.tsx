"use client";

import ReactDiffViewer from "react-diff-viewer-continued";
import type { TypeLinkDifferentResponse } from "../types/differentf.types";

export default function DiffView({ schema, different }: TypeLinkDifferentResponse) {
	return (
		<ReactDiffViewer oldValue={schema} newValue={different} splitView={true} />
	);
}
