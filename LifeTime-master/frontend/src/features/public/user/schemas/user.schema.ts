import * as v from 'valibot'
import {EmailSchema} from "@/shared/schemas/input.schema";
import {UserRoleEnum} from "@/features/public/user/types/user.types";
import {TariffSchemaResponse} from "@/features/public/tariff/schemas/tariff.schema";

export const UserSchemaResponse = v.object({
    id: v.pipe(v.number()),
    email: EmailSchema,
    tariff: TariffSchemaResponse,
    full_name: v.pipe(v.string()),
    role: v.pipe(v.enum(UserRoleEnum)),
    last_login_at: v.pipe(v.string(), v.isoTimestamp())
})