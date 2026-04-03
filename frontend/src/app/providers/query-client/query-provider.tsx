import type {PropsWithChildren} from "react";
import {getQueryClient} from "@/app/providers/query-client/query-client";
import {QueryClientProvider} from "@tanstack/react-query";


export function QueryProvider({children}: PropsWithChildren) {
    const queryClient = getQueryClient()

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    )
}
