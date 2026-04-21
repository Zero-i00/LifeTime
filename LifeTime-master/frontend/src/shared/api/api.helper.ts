import type {AxiosRequestHeaders} from "axios";


export const APP_API_HEADER: Partial<AxiosRequestHeaders> = {
    'Content-Type': 'application/json',
    'X-App-Context': 'AppFrontend'
}
