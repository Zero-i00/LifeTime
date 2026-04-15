import {AxiosError} from "axios";
import {SOMETHING_WRONG} from "@/shared/constants/error.constants";


export function extractError(error: Error): string {
    if (error instanceof AxiosError) {
        const detail = error.response?.data?.detail
        if (Array.isArray(detail)) {
            return detail.map((d: { msg?: string }) => d.msg ?? SOMETHING_WRONG).join(', ')
        }
        return detail ?? SOMETHING_WRONG
    }

    return error.message
}
