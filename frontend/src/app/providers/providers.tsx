'use client'

import type {PropsWithChildren} from "react";
import {QueryProvider} from "@/app/providers/query-client";


export function Providers({children}: PropsWithChildren) {
    return (
        <QueryProvider>
            {children}
        </QueryProvider>
    )
}
