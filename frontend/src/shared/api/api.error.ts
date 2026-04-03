import {AxiosError} from "axios";
import {SOMETHING_WRONG} from "@/shared/constants/error.constants";


export function extractError(error: Error): string {
    if (error instanceof AxiosError) {
        return error.response?.data?.detail ?? SOMETHING_WRONG
    }

    return error.message
}
