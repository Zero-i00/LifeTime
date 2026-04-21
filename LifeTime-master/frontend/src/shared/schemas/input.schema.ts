import * as v from "valibot";
import {INVALID_EMAIL_PATTERN, INVALID_PASSWORD_PATTERN} from "@/shared/constants/error.constants";
import {PASSWORD_PATTERN} from "@/shared/constants/regex.constants";


export const EmailSchema = v.pipe(v.string(), v.email(INVALID_EMAIL_PATTERN))
export const PasswordSchema =  v.pipe(v.string(), v.regex(PASSWORD_PATTERN, INVALID_PASSWORD_PATTERN))
