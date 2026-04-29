import {
    queryOptions,
    type UseMutationOptions,
    type UseQueryOptions,
} from "@tanstack/react-query"
import { getQueryClient } from "@/app/providers/query-client"
import { linkService } from "../services/link.service"
import type { Link, LinkRequest } from "../types/link.types"

class LinkQueries {
    public BASE_KEY = "links";

    list() {
        return queryOptions({
            queryKey: [this.BASE_KEY],
            queryFn: () => linkService.list(),
        })
    }

    retrieve(id: string) {
        return queryOptions({
            queryKey: [this.BASE_KEY, id],
            queryFn: () => linkService.retrieve(id),
        })
    }

    create(): UseMutationOptions<Link, Error, LinkRequest> {
        const queryClient = getQueryClient()

        return {
            mutationKey: [this.BASE_KEY, "create"],
            mutationFn: linkService.create,
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: [this.BASE_KEY] })
            },
        }
    }

    update(id: string): UseMutationOptions<Link, Error, LinkRequest> {
        const queryClient = getQueryClient()

        return {
            mutationKey: [this.BASE_KEY, "update", id],
            mutationFn: (data) => linkService.update(id, data),
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: [this.BASE_KEY] })
            },
        }
    }

    destroy(id: string): UseMutationOptions<void, Error, void> {
        const queryClient = getQueryClient()

        return {
            mutationKey: [this.BASE_KEY, "destroy", id],
            mutationFn: () => linkService.destroy(id),
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: [this.BASE_KEY] })
            },
        }
    }
}

export const linkQueries = new LinkQueries()
