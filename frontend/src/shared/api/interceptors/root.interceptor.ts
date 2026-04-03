import axios, {type CreateAxiosDefaults} from "axios";
import {API_SERVER_URL} from "@/shared/configs/api.config";
import {APP_API_HEADER} from "@/shared/api/api.helper";


const options: CreateAxiosDefaults = {
    baseURL: API_SERVER_URL,
    headers: APP_API_HEADER,
    withCredentials: true
}

export const axiosClient = axios.create(options)
