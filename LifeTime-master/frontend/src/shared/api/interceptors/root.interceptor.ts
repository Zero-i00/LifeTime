import axios, {type CreateAxiosDefaults} from "axios";
import {API_SERVER_URL} from "@/shared/configs/api.config";
import {APP_API_HEADER} from "@/shared/api/api.helper";
import {tokenService} from "@/shared/services/token.service";


const options: CreateAxiosDefaults = {
    baseURL: API_SERVER_URL,
    headers: APP_API_HEADER,
    withCredentials: true
}

export const axiosClient = axios.create(options)

axiosClient.interceptors.request.use(config => {
    const token = tokenService.get()

    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }

    return config
})
